#! /usr/bin/env python3

import usb

from yak_server import usbdevice
from yak_server import interface

class Application:
    """Object holding the main application state and main loop."""
    def setup(self):
        """Setup the application in preparation for the main loop."""
        switch_device = usbdevice.find(vendor_id=0x04d8, product_id=0x5900)[0]
        self.switch_interface = interface.USBInterface(switch_device)
        self.switch_interface.initialize()

        AC_device = usbdevice.find(vendor_id=0x04d8, product_id=0x5901)[0]
        self.AC_interface = interface.USBInterface(AC_device)
        self.AC_interface.initialize()

    def main_loop(self):
        """Run the program untill the server stops."""
        while self.server_running():
            self.main_loop_iteration()

    def server_running(self):
        """Return True if the server is running, False otherwise."""
        return True

    def main_loop_iteration(self):
        """Execute one iteration of the main loop."""
        event = self.get_event()
        self.handle_event(event)

    def get_event(self):
        """Get the next event.
        
        If there is no event to be processed, block untill one becomes
        available.
        """
        return self.switch_interface.get_event2()

    def handle_event(self, event):
        """Handle an event."""
        if event:
            self.AC_interface.send_command2(event)


def main():
    application = Application()
    application.setup()
    application.main_loop()

if __name__ == '__main__':
    main()
