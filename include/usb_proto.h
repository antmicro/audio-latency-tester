#ifndef _USB_PROTO_H_
#define _USB_PROTO_H_

#define USB_BULK_PACKET_SIZE 	64
#define USB_TRANSFERS_COUNT(x)	(1 + (x - 1) / USB_BULK_PACKET_SIZE)

typedef struct __attribute__((packed)) {
	uint32_t id;
	uint32_t sample_count;
	uint32_t sample_rate;
	uint32_t sample_depth;
	uint32_t channels_count;
	uint32_t volume_multiplier;
	uint32_t use_trigger;
	uint32_t padding[10];
} cfg_packet_t;

typedef struct __attribute__((packed)) {
	uint32_t id;
	uint32_t timestamps_count;
	uint32_t padding[14];
} timestamp_packet_t;

#define CFG_PACKET_MAGIC_HDR 		0x50534341
#define TIMESTAMP_PACKET_MAGIC_HDR 	0x50534342

#endif
