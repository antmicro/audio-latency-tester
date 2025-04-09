#include <stdlib.h>
#include <stdio.h>

#include <bsp/board.h>
#include <tusb.h>

#include <hardware/uart.h>
#include <pico/stdlib.h>

#include "hardware/clocks.h"
#include "hardware/structs/clocks.h"

#include "pico/audio_i2s.h"

#include "usb_proto.h"

// 1s of 48 kHz samples
#define MAX_SAMPLE_COUNT	48000
#define MAX_BYTES_PER_SAMPLE	2
#define MAX_CHANNEL_COUNT	2

#define SAMPLES_PER_BUFFER	32

#define RX_DATA_SIZE		(MAX_SAMPLE_COUNT * MAX_CHANNEL_COUNT * MAX_BYTES_PER_SAMPLE)

uint8_t rx_data[RX_DATA_SIZE];
uint64_t timestamps[MAX_SAMPLE_COUNT / SAMPLES_PER_BUFFER];

enum stream_state {
	IDLE,
	TRANSFER,
	STREAMING,
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

static struct audio_buffer_pool *init_audio(void)
{
	static audio_format_t audio_format = {
		.format = AUDIO_BUFFER_FORMAT_PCM_S16,
		.sample_freq = 44100,
		.channel_count = 2,
	};

	static struct audio_buffer_format producer_format = {
		.format = &audio_format,
		.sample_stride = 4
	};

	struct audio_buffer_pool *producer_pool =
		audio_new_producer_pool(&producer_format, 8,
			  SAMPLES_PER_BUFFER);
	bool __unused ok;
	const struct audio_format *output_format;
	struct audio_i2s_config config = {
		.data_pin = PICO_AUDIO_I2S_DATA_PIN,
		.clock_pin_base = PICO_AUDIO_I2S_CLOCK_PIN_BASE,
		.dma_channel = 0,
		.pio_sm = 0,
	};

	output_format = audio_i2s_setup(&audio_format, &config);
	if (!output_format) {
		panic("Unable to open audio device.\n");
	}

	ok = audio_i2s_connect(producer_pool);
	assert(ok);
	audio_i2s_set_enabled(true);

	return producer_pool;
}

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

static void trigger_audio_capture()
{
	gpio_put(GPIO_TRIGGER_PIN, 0);
	// wait a bit to make sure the other side reads the state
	for (int i = 0; i < 30; i++)
		;
	gpio_put(GPIO_TRIGGER_PIN, 1);
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
			printf("use_trigger: %d\r\n", cfg_packet.use_trigger);

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

				// Update sample rate, cast is needed to override const
				((struct audio_format *) sd->audio_buffer_pool->format)->sample_freq = sd->sample_rate;

				printf("configuration passed!\r\n");

				memset(rx_data, 0x00, sizeof(rx_data));
				memset(timestamps, 0x00, sizeof(timestamps));

				sd->state = TRANSFER;
			} else {
				printf("configuration failed!\r\n");
			}
		} else {
			printf("expected cfg packet!\r\n");
		}
		break;
	}
	case TRANSFER:
	{
		int rx_len =
			sd->sample_count *
			sd->sample_depth *
			sd->channels_count;

		for (int i = 0; i < USB_TRANSFERS_COUNT(rx_len); i++) {
			usb_read(&rx_data[i * USB_BULK_PACKET_SIZE], USB_BULK_PACKET_SIZE);
		}

		sd->state = STREAMING;
		break;
	}
	case STREAMING:
	{
		int buffer_count =  1 + ((sd->sample_count - 1) / (SAMPLES_PER_BUFFER));

		for (int j = 0; j < buffer_count; j++) {

			struct audio_buffer *buffer = take_audio_buffer(sd->audio_buffer_pool, true);

			int16_t *samples_src = (int16_t *)rx_data + SAMPLES_PER_BUFFER * j * 2;
			int16_t *samples_dst = (int16_t *)buffer->buffer->bytes;

			buffer->sample_count = SAMPLES_PER_BUFFER;
			assert(buffer->sample_count);
			assert(buffer->max_sample_count >= audio_buffer->sample_count);

			for (int i = 0; i < SAMPLES_PER_BUFFER * 2; i++) {
				samples_dst[i] = (int16_t) ((samples_src[i] * sd->volume_multiplier) >> 15u);
			}

			if (sd->use_trigger) {
				trigger_audio_capture();
			}
			timestamps[j] = time_us_64();
			give_audio_buffer(sd->audio_buffer_pool, buffer);
		}

		timestamp_packet_t ts_packet = {
			.id = TIMESTAMP_PACKET_MAGIC_HDR,
			.timestamps_count =  buffer_count,
		};

		usb_write((uint8_t *) &ts_packet, sizeof(ts_packet));

		printf("USB transfers count: %d\r\n", USB_TRANSFERS_COUNT(buffer_count * 8));

		for (int j = 0; j < USB_TRANSFERS_COUNT(buffer_count * 8); j++) {
			usb_write(&timestamps[j * 8], USB_BULK_PACKET_SIZE);
		}

		printf("stream finished, return to idle\r\n");

		sd->state = IDLE;
		break;
	}
	default:

		printf("unknown state, reverting to idle\r\n");
		sd->state = IDLE;
		break;
	}
}

int main(void)
{
	struct stream_desc sd;

	// GPIO set only required for the Adafruit Prop Maker board
	gpio_init(GPIO_MAX98357_ENABLE);
	gpio_set_dir(GPIO_MAX98357_ENABLE, GPIO_OUT);
	gpio_put(GPIO_MAX98357_ENABLE, 1);

	// Two RP2040's are connected via GPIO20.
	// Let's use it to trigger the audio_in firmware to start recording audio.
	gpio_init(GPIO_TRIGGER_PIN);
	gpio_set_dir(GPIO_TRIGGER_PIN, GPIO_OUT);
	gpio_put(GPIO_TRIGGER_PIN, 1);

	board_init();
	stdio_init_all();

	// Initialize TinyUSB
	tud_init(0);

	sd.audio_buffer_pool = init_audio();
	sd.state = IDLE;

	while (1) {
		vendor_task(&sd);
	}

	return 0;
}
