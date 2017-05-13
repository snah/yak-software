/*
 * File:   main.c
 * Author: Hans
 *
 * Created on May 7, 2017, 9:05 PM
 */

#include "main.h"

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


void interrupt isr()
{
	usb_service();
}

void main()
{
	setup();

	uint8_t len;
	const unsigned char *data;

	TRISAbits.TRISA5 = 0;
	LATAbits.LATA5 = 1;

	while (1)
	{
		if (usb_is_configured() && usb_out_endpoint_has_data(1))
		{
			len = usb_get_out_buffer(1, &data);
			if (data[0])
			{
				LATAbits.LATA5 = 1;
			}
			else
			{
				LATAbits.LATA5 = 0;
			}
			usb_arm_out_endpoint(1);
		}
	}
}

void setup()
{
	OSCCONbits.IRCF = 0b1111; // 16MHz HFINTOSC postscaler.

	// Setup USB clock-tuning.
	ACTCONbits.ACTSRC = 1;
	ACTCONbits.ACTEN = 1;

	// Enable interrupts.
	INTCONbits.PEIE = 1;
	INTCONbits.GIE = 1;

	usb_init();
}
