/* 
 * File:   usb_config.h
 * Author: hans
 *
 * Created on May 7, 2017, 9:18 PM
 */

#ifndef USB_CONFIG_H
#define	USB_CONFIG_H

//////////////////////////
// Settings for the USB stack.

#define NUM_ENDPOINT_NUMBERS 1		// Number of enpoints excluding endpoint 0.

#define EP_0_LEN 8					// Endpoint zero max packet length.

#define EP_1_OUT_LEN 8				// Endpoint one max out packet length.
#define EP_1_IN_LEN 8				// Endpoint one max in packet length

#define NUMBER_OF_CONFIGURATIONS 1	// Number of different configurations.

#define PPB_MODE PPB_NONE			// No ping-pong buffering.

#define USB_USE_INTERRUPTS			// Use interrupts instead of polling.

//////////////////////////
// Other settings.

#define ID_VENDOR 0x04D8
#define ID_PRODUCT 0x5900
#define DEVICE_VERSION 0x0001

#define USB_VERSION 0x0200			// USB 2.0

// Zero indicates class defined in other descriptors.
#define DEVICE_CLASS 0x00
#define DEVICE_SUBCLASS 0x00
#define DEVICE_PROTOCOL 0x00

#define EP_0_MAX_PACKET_LENGTH EP_1_IN_LEN	// Use value as defined above.

#define NUMBER_OF_INTERFACES 1

#define CONFIGURATION_INDEX 1
#define SELF_POWERED 0x80
#define MAX_CURRENT 50	// 50*2 = 10mA.

#define INTERFACE_INDEX 0
#define ALTERNATIVE_SETTING_INDEX 0
#define NUMBER_OF_ENDPOINTS NUM_ENDPOINT_NUMBERS
#define VENDOR_SPECIFIC_INTERFACE_CLASS 0
#define INTERFACE_SUBCLASS 0
#define INTERFACE_PROTOCOL 0

#define ENDPOINT_ADDRESS 1
#define ENDPOINT_DIRECTION_OUT 0
#define ENDPOINT_DIRECTION_IN 0x80
#define ENDPOINT_1_MAX_PACKET_SIZE EP_1_IN_LEN
#define ENDPOINT_1_POLLING_INTERVAL 10	// ms.

//////////////////////////
// Descriptor string related.

#define NO_STRING 0
#define LANGUAGE_META_STRING_INDEX 0
#define VENDOR_STRING_INDEX 1
#define PRODUCT_STRING_INDEX 2

#endif	/* USB_CONFIG_H */

