/*
 * File:   main.c
 * Author: Hans
 *
 * Created on May 7, 2017, 9:05 PM
 */

#include <xc.h>
#include <string.h>
#pragma warning disable 520
#include "usb.h"
#include "usb_ch9.h"

#pragma config FOSC = INTOSC
#pragma config WDTE = OFF
#pragma config PWRTE = OFF
#pragma config MCLRE = ON
#pragma config CP = OFF
#pragma config BOREN = ON
#pragma config CLKOUTEN = OFF
#pragma config IESO = OFF
#pragma config FCMEN = OFF
#pragma config WRT = OFF
#pragma config CPUDIV = NOCLKDIV
#pragma config USBLSCLK = 48MHz
#pragma config PLLMULT = 3x
#pragma config PLLEN = ENABLED
#pragma config STVREN = ON
#pragma config BORV = LO
#pragma config LPBOR = ON
#pragma config LVP = ON

void main(void) {
	OSCCONbits.IRCF = 0b1111; // 16MHz HFINTOSC postscalar

	// Setup USB clock-tuning.
	ACTCONbits.ACTSRC = 1;
	ACTCONbits.ACTEN = 1;

	// Enable interrupts.
	INTCONbits.PEIE = 1;
	INTCONbits.GIE = 1;
    
	// Setup pins.
    ANSELC = 0;
    TRISCbits.TRISC2 = 1;

	usb_init();

	while (1) {
		if (usb_is_configured() &&
		    !usb_in_endpoint_halted(1) &&
		    !usb_in_endpoint_busy(1)) {

			unsigned char *buf = usb_get_in_buffer(1);
			
            if (PORTCbits.RC2)
                buf[0] = 0x01;
            else
                buf[0] = 0x00;
			usb_send_in_buffer(1, 1);
		}
	}
}

/* Callbacks. These function names are set in usb_config.h. */
void SET_CONFIGURATION_CALLBACK(uint8_t configuration)
{

}
uint16_t GET_DEVICE_STATUS_CALLBACK()
{
	return 0x0000;
}

void ENDPOINT_HALT_CALLBACK(uint8_t endpoint, bool halted)
{

}

int8_t SET_INTERFACE_CALLBACK(uint8_t interface, uint8_t alt_setting)
{
	return 0;
}

int8_t GET_INTERFACE_CALLBACK(uint8_t interface)
{
	return 0;
}

void OUT_TRANSACTION_CALLBACK(uint8_t endpoint)
{

}

void IN_TRANSACTION_COMPLETE_CALLBACK(uint8_t endpoint)
{

}

static char buf[512];

static int8_t data_cb(bool transfer_ok, void *context)
{
	/* For OUT control transfers, data from the data stage of the request
	 * is in buf[]. */
	return 0;
}

int8_t UNKNOWN_SETUP_REQUEST_CALLBACK(const struct setup_packet *setup)
{
#define MIN(X,Y) ((X)<(Y)?(X):(Y))

	/* This handler handles request 254/dest=other/type=vendor only.*/
	if (setup->bRequest != 245 ||
	    setup->REQUEST.destination != 3 /*other*/ ||
	    setup->REQUEST.type != 2 /*vendor*/)
		return -1;

	if (setup->REQUEST.direction == 0/*OUT*/) {
		if (setup->wLength == 0) {
			/* There will be NO data stage. This sends back the
			 * STATUS stage packet. */
			usb_send_data_stage(NULL, 0, data_cb, NULL);
		}
		memset(buf,0,sizeof(buf));

		/* Set up an OUT data stage (we will receive data) */
		if (setup->wLength > sizeof(buf)) {
			/* wLength is too big. Return -1 to
			   refuse this transfer*/
			return -1;
		}
		usb_start_receive_ep0_data_stage(buf, setup->wLength, &data_cb, NULL);
	}
	else {
		/* Direction is 1 (IN) */
		size_t i;

		for (i = 0; i < sizeof(buf); i++) {
			buf[i] = sizeof(buf)-i;
		}

		/* Set up an OUT data stage (we will receive data) */
		if (setup->wLength > sizeof(buf)) {
			/* wLength is too big. Return -1 to
			   refuse this transfer*/
			return -1;
		}
		usb_send_data_stage(buf ,setup->wLength, data_cb, NULL);
	}

	return 0; /* 0 = can handle this request. */
#undef MIN
}

int16_t UNKNOWN_GET_DESCRIPTOR_CALLBACK(const struct setup_packet *pkt, const void **descriptor)
{
	return -1;
}

void START_OF_FRAME_CALLBACK(void)
{

}

void USB_RESET_CALLBACK(void)
{

}

#ifdef _PIC14E
void interrupt isr()
{
	usb_service();
}
#elif _PIC18

#ifdef __XC8
void interrupt high_priority isr()
{
	usb_service();
}
#elif _PICC18
#error need to make ISR
#endif

#endif
