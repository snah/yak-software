#include "usb.h"
#include "usb_ch9.h"

#include "usb_config.h"

struct configuration_packet {
	struct configuration_descriptor  config;
	struct interface_descriptor      interface;
	struct endpoint_descriptor       ep1_in;
};


const struct device_descriptor this_device_descriptor =
{
	sizeof(this_device_descriptor), // bLength.
	DESC_DEVICE,					// bDescriptorType.
	0x0200,							// bcdUSB (USB 2.0).
	0x00,							// bDeviceClass.
	0x00,							// bDeviceSubClass.
	0x00,							// bProtocol.
	EP_0_LEN,						// bMaxPacketSize0.
	0xA0A0,							// idVendor.
	0x0001,							// idProduct.
	0x0001,							// bcdDevice (1.0).
	1,								// iManufacturer.
	2,								// iProduct.
	0,								// iSerialNumber.
	NUMBER_OF_CONFIGURATIONS		// bNumConfigurations
};

static const struct configuration_packet configuration =
{
	{
	sizeof(struct configuration_descriptor),	// bLength.
	DESC_CONFIGURATION,							// bDescriptorType.
	sizeof(configuration),					// wTotalLength.
	1,											// bNumInterfaces.
	1,											// bConfigurationValue.
	2,											// iConfiguration.
	0x80,										// bmAttributes.
	100/2,										// MaxPower = 100/2 -> 100mA.
	},

	{

	sizeof(struct interface_descriptor),		// bLength.
	DESC_INTERFACE,								// bDescriptorType.
	0x0,										// InterfaceNumber.
	0x0,										// AlternateSetting.
	NUM_ENDPOINT_NUMBERS,						// bNumEndpoints.
	0xff,										// bInterfaceClass.
	0x00,										// bInterfaceSubclass.
	0x00,										// bInterfaceProtocol.
	0x00,										// iInterface.
	},

	{

	sizeof(struct endpoint_descriptor),			// bLength
	DESC_ENDPOINT,								// bDescriptorType.
	0x01 | 0x80,								// bEndpointAddress = 1 | 0x80=IN
	EP_INTERRUPT,								// bmAttributes.
	64,											// wMaxPacketSize.
	10,											// bInterval in ms.
	},
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

static const struct {uint8_t bLength;uint8_t bDescriptorType; uint16_t chars[20]; } product_string = {
	sizeof(product_string),
	DESC_STRING,
	{'Y','a','k',' ','S','w','i','t','c','h',' ','i','n','t','e','r','f','a','c','e'}
};

int16_t usb_application_get_string(uint8_t string_number, const void **ptr)
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

const struct configuration_descriptor *usb_application_config_descs[] =
{
	(struct configuration_descriptor*) &configuration,
};
