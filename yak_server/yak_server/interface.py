"""Devices various interfaces that are connected to the server."""

from yak_server import usbdevice
from yak_server import translators


class Interface:
    """Abstract interface class.

    An interface is any object that allows the server to communicate
    with the outside world.

    Subclasses should at least implement 'get_event' and
    'send_command'.
    """

    def initialize(self):
        """Initialize the interface so it is ready to use."""

    def get_event(self):
        """Return the next event from the interface.

        Subclasses should overwrite this.
        """
        raise NotImplementedError()

    def send_command(self, command):
        """Send a command to the interface.

        Subclasses should overwrite this.
        """
        raise NotImplementedError()


class USBInterface(Interface):
    """An interface that is connected to a USB device."""

    def __init__(self, usb_device, translator):
        """Create an interface from the given USB device."""
        self._usb_device = usb_device
        self.translator = translator

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
        maximum_data_length = self.translator.maximum_data_length()
        return self._usb_device.read(maximum_data_length)

    def _write_data_to_device(self, data):
        self._usb_device.write(data)


class InterfaceManager:
    """Manages the various interfaces of the server."""

    @classmethod
    def input_interfaces(cls):
        """Return an iterable of all input devices."""
        devices = usbdevice.find(vendor_id=0x04d8, product_id=0x5900)
        return [cls._make_interface(device) for device in devices]

    @classmethod
    def output_interfaces(cls):
        """Return an iterable of all output devices."""
        devices = usbdevice.find(vendor_id=0x04d8, product_id=0x5901)
        return [cls._make_interface(device) for device in devices]

    @classmethod
    def _make_interface(cls, device):
        return USBInterface(device, translators.make_usb_translator(device))
