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

	while (1)
	{
		if (usb_is_configured() && endpoint_ready())
		{
			t_state state = get_state();
			send_state_if_changed(state);
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
    
	// Setup pins.
    ANSELC = 0;
    TRISCbits.TRISC2 = 1;

	usb_init();
}

t_state get_state()
{
	return PORTCbits.RC2;
}

void send_state_if_changed(unsigned char state)
{
	static t_state last_state = 0xff;

	if (state != last_state)
	{
		send_state(state);
		last_state = state;
	}
}

void send_state(t_state state)
{
	unsigned char *buffer = usb_get_in_buffer(1);

	buffer[0] = state;
	usb_send_in_buffer(1, 1);
}

bool endpoint_ready()
{
   return !usb_in_endpoint_halted(1) && !usb_in_endpoint_busy(1);
}
