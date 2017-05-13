#include "usb.h"
#include "usb_ch9.h"

#include "usb_config.h"


const struct device_descriptor USB_DEVICE_DESCRIPTOR =
{
	sizeof(USB_DEVICE_DESCRIPTOR),
	DESC_DEVICE,
	USB_VERSION,
	DEVICE_CLASS,
	DEVICE_SUBCLASS,
	DEVICE_PROTOCOL,
	EP_0_MAX_PACKET_LENGTH,
	ID_VENDOR,
	ID_PRODUCT,
	DEVICE_VERSION,
	VENDOR_STRING_INDEX,
	PRODUCT_STRING_INDEX,
	NO_STRING,
	NUMBER_OF_CONFIGURATIONS
};


struct configuration_packet {
	struct configuration_descriptor  config;
	struct interface_descriptor      interface;
	struct endpoint_descriptor       ep1_in;
};

static const struct configuration_packet configuration =
{
	{
		sizeof(struct configuration_descriptor),
		DESC_CONFIGURATION,
		sizeof(configuration),
		NUMBER_OF_INTERFACES,
		CONFIGURATION_INDEX,
		NO_STRING,
		SELF_POWERED,
		MAX_CURRENT
	},

	{
	sizeof(struct interface_descriptor),
		DESC_INTERFACE,
		INTERFACE_INDEX,
		ALTERNATIVE_SETTING_INDEX,
		NUMBER_OF_ENDPOINTS,
		VENDOR_SPECIFIC_INTERFACE_CLASS,
		INTERFACE_SUBCLASS,
		INTERFACE_PROTOCOL,
		NO_STRING
	},

	{
		sizeof(struct endpoint_descriptor),
		DESC_ENDPOINT,
		ENDPOINT_ADDRESS | ENDPOINT_DIRECTION_OUT,
		EP_INTERRUPT,
		ENDPOINT_1_MAX_PACKET_SIZE,
		ENDPOINT_1_POLLING_INTERVAL
	}
};

static const struct {uint8_t bLength;uint8_t bDescriptorType; uint16_t lang; } str00 = {
	sizeof(str00),
	DESC_STRING,
	0x0409 // US English
};

static const struct {uint8_t bLength;uint8_t bDescriptorType; uint16_t chars[4]; } vendor_string = {
	sizeof(vendor_string),
	DESC_STRING,
	{'Y','a','k','.'}
};

static const struct {uint8_t bLength;uint8_t bDescriptorType; uint16_t chars[18]; } product_string = {
	sizeof(product_string),
	DESC_STRING,
	{'Y','a','k',' ','2','3','0','V',' ','i','n','t','e','r','f','a','c','e'}
};

int16_t USB_STRING_DESCRIPTOR_FUNC(uint8_t string_number, const void **ptr)
{
	if (string_number == 0) {
		*ptr = &str00;
		return sizeof(str00);
	}
	else if (string_number == 1) {
		*ptr = &vendor_string;
		return sizeof(vendor_string);
	}
	else if (string_number == 2) {
		*ptr = &product_string;
		return sizeof(product_string);
	}

	return -1;
}

const struct configuration_descriptor *USB_CONFIG_DESCRIPTOR_MAP[] =
{
	(struct configuration_descriptor*) &configuration,
};
