from yak_server import usbdevice

class USBInterface:
    """An interface that is connected to a USB device."""
    def __init__(self, usb_device):
        self._usb_device = usb_device

    def initialize(self):
        """Setup the interface so it is ready to use."""
        self._usb_device.connect()

    def get_event2(self):
        """Return the next event from the interface.
        
        If there is no event to be processed, block untill one becomes
        available.

        This is a temporary function that returns the raw data instead
        of a proper event. Once events are implemented this function
        will be removed.
        """
        return self._usb_device.read(1)

    def send_command2(self, command):
        """Send a command to the interface.

        This is a temporary function that expects the raw data instead
        of a proper command. Once commands are implemented this
        function will be removed.
        """
        self._usb_device.write(command)


class InterfaceManager():
    def input_interfaces(self):
        """Return an iterable of all input devices."""
        devices = usbdevice.find(vendor_id=0x04d8, product_id=0x5900)
        return [USBInterface(device) for device in devices]

    def output_interfaces(self):
        """Return an iterable of all output devices."""
        devices = usbdevice.find(vendor_id=0x04d8, product_id=0x5901)
        return [USBInterface(device) for device in devices]
