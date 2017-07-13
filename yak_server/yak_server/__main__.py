#! /usr/bin/env python3

import usb

from yak_server import usbdevice
from yak_server import interface

class Application:
    """Object holding the main application state and main loop."""
    def setup(self):
        """Setup the application in preparation for the main loop."""
        interface_manager = interface.InterfaceManager()
        self.switch_interface = interface_manager.input_interfaces()[0]
        self.switch_interface.initialize()

        self.AC_interface = interface_manager.output_interfaces()[0]
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
