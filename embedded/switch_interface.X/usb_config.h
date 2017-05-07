/* 
 * File:   usb_config.h
 * Author: hans
 *
 * Created on May 7, 2017, 9:18 PM
 */

#ifndef USB_CONFIG_H
#define	USB_CONFIG_H

#define NUM_ENDPOINT_NUMBERS 1		// Excludes endpoint 0

/* Only 8, 16, 32 and 64 are supported for endpoint zero length. */
#define EP_0_LEN 8

#define EP_1_OUT_LEN 64
#define EP_1_IN_LEN 64

#define EP_2_OUT_LEN 64
#define EP_2_IN_LEN 64

#define NUMBER_OF_CONFIGURATIONS 1

/* Ping-pong buffering mode. Valid values are:
	PPB_NONE         - Do not ping-pong any endpoints
	PPB_EPO_OUT_ONLY - Ping-pong only endpoint 0 OUT
	PPB_ALL          - Ping-pong all endpoints
	PPB_EPN_ONLY     - Ping-pong all endpoints except 0
*/
#ifdef __PIC32MX__
	/* PIC32MX only supports PPB_ALL */
	#define PPB_MODE PPB_ALL
#else
	#define PPB_MODE PPB_NONE
#endif

/* Comment the following line to use polling USB operation. When using polling,
   You are responsible for calling usb_service() periodically from your
   application. */
#define USB_USE_INTERRUPTS

/* Objects from usb_descriptors.c */
#define USB_DEVICE_DESCRIPTOR this_device_descriptor
#define USB_CONFIG_DESCRIPTOR_MAP usb_application_config_descs
#define USB_STRING_DESCRIPTOR_FUNC usb_application_get_string

/* The Setup Request number (bRequest) to tell the host to use for the
 * Microsoft descriptors. See docs/winusb.txt for details. */
#define MICROSOFT_OS_DESC_VENDOR_CODE 0x50
/* Automatically send the descriptors to bind the WinUSB driver on Windows */
#define AUTOMATIC_WINUSB_SUPPORT

/* Optional callbacks from usb.c. Leave them commented if you don't want to
   use them. For the prototypes and documentation for each one, see usb.h. */

#define SET_CONFIGURATION_CALLBACK app_set_configuration_callback
#define GET_DEVICE_STATUS_CALLBACK app_get_device_status_callback
#define ENDPOINT_HALT_CALLBACK     app_endpoint_halt_callback
#define SET_INTERFACE_CALLBACK     app_set_interface_callback
#define GET_INTERFACE_CALLBACK     app_get_interface_callback
#define OUT_TRANSACTION_CALLBACK   app_out_transaction_callback
#define IN_TRANSACTION_COMPLETE_CALLBACK   app_in_transaction_complete_callback
#define UNKNOWN_SETUP_REQUEST_CALLBACK app_unknown_setup_request_callback
#define UNKNOWN_GET_DESCRIPTOR_CALLBACK app_unknown_get_descriptor_callback
#define START_OF_FRAME_CALLBACK    app_start_of_frame_callback
#define USB_RESET_CALLBACK         app_usb_reset_callback

#endif	/* USB_CONFIG_H */

