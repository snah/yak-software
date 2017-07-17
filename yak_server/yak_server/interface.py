"""Devices various interfaces that are connected to the server."""

from yak_server import usbdevice
from yak_server import translator


class USBInterface:
    """An interface that is connected to a USB device."""

    translator = translator.SwitchInterfaceTranslator()

    def __init__(self, usb_device):
        """Create an interface from the given USB device."""
        self._usb_device = usb_device

    def initialize(self):
        """Initialize the interface so it is ready to use."""
        self._usb_device.connect()

    def get_event(self):
        """Return the next event from the interface."""
        data = self._read_data_from_device()
        event = self.translator.raw_data_to_event(data)
        return event

    def send_command(self, command):
        """Send a command to the interface."""
        data = self.translator.event_to_raw_data(command)
        self._write_data_to_device(data)

    def _read_data_from_device(self):
        return self._usb_device.read(1)

    def _write_data_to_device(self, data):
        self._usb_device.write(data)


class InterfaceManager():
    """Manages the various interfaces of the server."""

    def input_interfaces(self):
        """Return an iterable of all input devices."""
        devices = usbdevice.find(vendor_id=0x04d8, product_id=0x5900)
        return [USBInterface(device) for device in devices]

    def output_interfaces(self):
        """Return an iterable of all output devices."""
        devices = usbdevice.find(vendor_id=0x04d8, product_id=0x5901)
        return [USBInterface(device) for device in devices]
