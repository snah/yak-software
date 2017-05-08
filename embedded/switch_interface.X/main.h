#ifndef MAIN_H
#define	MAIN_H

typedef unsigned char t_state;

t_state get_state();
void setup();
void send_state(t_state state);
void send_state_if_changed(unsigned char state);
unsigned char endpoint_ready();

#endif
