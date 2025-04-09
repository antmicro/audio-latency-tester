#include <stdlib.h>
#include <stdio.h>

#include <bsp/board.h>
#include <tusb.h>

#include <hardware/uart.h>
#include <pico/stdlib.h>

#include "hardware/clocks.h"
#include "hardware/structs/clocks.h"

#include "usb_proto.h"
#include "pdm_microphone/pdm_microphone.h"

#define MIC_SAMPLE_FREQ 16000

// 0.5 s of 48 kHz samples
#define MAX_SAMPLE_COUNT	64000
#define MAX_BYTES_PER_SAMPLE	2
#define MAX_CHANNEL_COUNT	1

#define SAMPLES_PER_BUFFER	16

#define RX_DATA_SIZE		(MAX_SAMPLE_COUNT * MAX_CHANNEL_COUNT * MAX_BYTES_PER_SAMPLE)

uint8_t rx_data[RX_DATA_SIZE];
uint64_t timestamps[MAX_SAMPLE_COUNT / SAMPLES_PER_BUFFER];

// configuration
const struct pdm_microphone_config config = {
#ifdef AUDIO_CONTROLLER_BOARD
    .gpio_data = 13, // GPIO pin for the PDM DAT signal
    .gpio_clk = 14, // GPIO pin for the PDM CLK signal
#else
    .gpio_data = 11, // GPIO pin for the PDM DAT signal
    .gpio_clk = 9, // GPIO pin for the PDM CLK signal
#endif
    .pio = pio0, // PIO instance to use
    .pio_sm = 0, // PIO State Machine instance to use
    .sample_rate = MIC_SAMPLE_FREQ, // sample rate in Hz
    .sample_buffer_size = SAMPLES_PER_BUFFER, // number of samples to buffer
};

int16_t sample_buffer[SAMPLES_PER_BUFFER];
volatile int samples_read = 0;

enum stream_state {
	IDLE,
	RECORDING,
	TRANSFER,
};

struct stream_desc {
	uint32_t length;
	uint32_t sample_count;
	uint32_t sample_rate;
	uint32_t sample_depth;
	uint32_t channels_count;
	uint32_t volume_multiplier;
	uint32_t use_trigger;

	enum stream_state state;
	struct audio_buffer_pool *audio_buffer_pool;
};

static void usb_housekeeping(void)
{
	tud_task();
	if (tud_suspended()) {
		tud_remote_wakeup();
	}
}

static uint32_t usb_read(void *buffer, uint32_t bufsize)
{
	uint32_t ret;

	while (!tud_vendor_available()) {
		usb_housekeeping();
	}

	ret = tud_vendor_read(buffer, bufsize);
	tud_vendor_read_flush();

	return ret;
}

static uint32_t usb_write(void const *buffer, uint32_t bufsize)
{
	uint32_t ret;

	while (tud_vendor_write_available() < 64)  {
		usb_housekeeping();
	}

	ret = tud_vendor_write(buffer, bufsize);
	tud_vendor_flush();

	return ret;
}

void wait_for_trigger() {
	// block until posedge
	while (gpio_get(GPIO_TRIGGER_PIN))
		;
	while (!gpio_get(GPIO_TRIGGER_PIN))
		;
}

static void vendor_task(struct stream_desc *sd)
{
	switch (sd->state) {

	case IDLE:
	{
		cfg_packet_t cfg_packet;

		usb_read(&cfg_packet, sizeof(cfg_packet));

		if (cfg_packet.id == CFG_PACKET_MAGIC_HDR) {
			printf("Configuration packet received\r\n");
			printf("stream length (samples): %d\r\n", cfg_packet.sample_count);
			printf("sample rate (bps): %d\r\n", cfg_packet.sample_rate);
			printf("sample depth (bits): %d\r\n", cfg_packet.sample_depth);
			printf("channels_count: %d\r\n", cfg_packet.channels_count);
			printf("volume multiplier: 0x%x\r\n", cfg_packet.volume_multiplier);
			printf("use trigger: %d\r\n", cfg_packet.use_trigger);

			if (cfg_packet.sample_count != 0 &&
					cfg_packet.sample_rate != 0 &&
					cfg_packet.sample_depth != 0 &&
					cfg_packet.channels_count != 0) {

				sd->sample_count = cfg_packet.sample_count;
				sd->sample_rate = cfg_packet.sample_rate;
				sd->sample_depth = cfg_packet.sample_depth;
				sd->channels_count = cfg_packet.channels_count;
				sd->volume_multiplier = cfg_packet.volume_multiplier;
				sd->use_trigger = cfg_packet.use_trigger;

				printf("configuration passed!\r\n");

				memset(rx_data, 0x00, sizeof(rx_data));
				memset(timestamps, 0x00, sizeof(timestamps));
        pdm_microphone_set_filter_volume(sd->volume_multiplier);

				sd->state = RECORDING;
			} else {
				printf("configuration failed!\r\n");
			}
		} else {
			printf("expected cfg packet!\r\n");
		}
		break;
	}
	case RECORDING:
	{
		if (sd->use_trigger) {
			printf("waiting for rising edge on GPIO%d\r\n", GPIO_TRIGGER_PIN);
			wait_for_trigger();
		}

		int buffer_count =  1 + ((sd->sample_count - 1) / (SAMPLES_PER_BUFFER));
    printf("buffer_count: %d\r\n", buffer_count);

		for (int j = 0; j < buffer_count; j++) {

      while (samples_read == 0) {
        tight_loop_contents();
      }
			timestamps[j] = time_us_64();

			int16_t *samples_dst = (int16_t *)rx_data + SAMPLES_PER_BUFFER * j;

			for (int i = 0; i < SAMPLES_PER_BUFFER; i++) {
				samples_dst[i] = sample_buffer[i];
			}

      samples_read = 0;
		}

    printf("End acquisition\r\n");

		sd->state = TRANSFER;
		break;
	}
	case TRANSFER:
	{
		int tx_len =
			sd->sample_count *
			sd->sample_depth *
			sd->channels_count;

		int timestamps_count =  1 + ((sd->sample_count - 1) / (SAMPLES_PER_BUFFER));

		printf("USB transfers count: %d\r\n", USB_TRANSFERS_COUNT(tx_len));

		for (int i = 0; i < USB_TRANSFERS_COUNT(tx_len); i++) {
			usb_write(&rx_data[i * USB_BULK_PACKET_SIZE], USB_BULK_PACKET_SIZE);
		}

		timestamp_packet_t ts_packet = {
			.id = TIMESTAMP_PACKET_MAGIC_HDR,
			.timestamps_count =  timestamps_count,
		};

		usb_write((uint8_t *) &ts_packet, sizeof(ts_packet));

		printf("buffer count: %d\r\n", timestamps_count);
		printf("USB transfers count (timestamps): %d\r\n", USB_TRANSFERS_COUNT(timestamps_count * 8));

		for (int j = 0; j < USB_TRANSFERS_COUNT(timestamps_count * 8); j++) {
			usb_write(&timestamps[j * 8], USB_BULK_PACKET_SIZE);
		}

		printf("Timestamps transfer finished\r\n");


		sd->state = IDLE;
		break;
	}
	default:

		printf("unknown state, reverting to idle\r\n");
		sd->state = IDLE;
		break;
	}
}

void on_pdm_samples_ready() {
  samples_read = pdm_microphone_read(sample_buffer, SAMPLES_PER_BUFFER);
}

int main(void)
{
	struct stream_desc sd;

	board_init();
	stdio_init_all();

	gpio_init(GPIO_TRIGGER_PIN);
	gpio_set_dir(GPIO_TRIGGER_PIN, GPIO_IN);

	// Initialize TinyUSB
	tud_init(0);

	sd.state = IDLE;

  pdm_microphone_init(&config);
  pdm_microphone_set_samples_ready_handler(on_pdm_samples_ready);
  pdm_microphone_start();


	while (1) {
		vendor_task(&sd);
	}

	return 0;
}
