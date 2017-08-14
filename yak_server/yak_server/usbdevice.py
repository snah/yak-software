"""Defines abstractions for USB devices."""


import logging
import usb

import ezvalue


_LOGGER = logging.getLogger(__name__)


class USBError(Exception):
    """Generic USB exception."""


class IncompleteUSBWrite(USBError):
    """Not all data could be written to the USB device."""


def _translate_search_parameters(search_parameters):
    """Translate search parameters into kwargs for pyusb."""
    parameter_translation_table = {'product_id': 'idProduct',
                                   'vendor_id': 'idVendor',
                                   'release_number': 'bcdDevice'}

    new_params = dict()

    for input_param, output_param in parameter_translation_table.items():
        try:
            new_params[output_param] = search_parameters[input_param]
        except KeyError:
            pass
    return new_params


def find(**search_parameters):
    """Return an iterable of USBDevices matching the search parameters.

    The search parameters are given as keyword arguments with
    string value. Currently supported search parameters are
    product_id, vendor_id and release_number, all of which
    expect an integer value.
    """
    _LOGGER.info('Scanning for usb devices with %s', search_parameters)

    find_kwargs = _translate_search_parameters(search_parameters)
    raw_devices = usb.core.find(**find_kwargs, find_all=True)

    devices = tuple(USBDevice(raw_device) for raw_device in raw_devices)

    for device in devices:
        _LOGGER.info('Found usb device: %s', device.device_info())

    return devices


def find_by_class_id(device_class_id):
    """Return an iterable of USBDevices with the given device class id."""
    search_parameters = {'vendor_id': device_class_id.vendor_id,
                         'product_id': device_class_id.product_id,
                         'release_number': device_class_id.release_number}
    return find(**search_parameters)


class DeviceClassID(ezvalue.Value):
    """A unique identifier for each usb device class.

    The id is composed of the vendor id, product id and device
    release number.
    """

    vendor_id = """Device vendor identifier (idVendor)."""
    product_id = """Product identifier of the device (idProduct)."""
    release_number = """Release number of the device (bcdDevice)"""


def _managed(message_template):
    """Manage execution of the decorated function.

    The function call will be logged and any exceptions from pyusb
    will be logged and reraised as our own USBError.
    """
    # pylint: disable = protected-access
    def outer(function):
        def wrapper(self, *args, **kwargs):
            _LOGGER.info(self._format_message(message_template))
            try:
                return function(self, *args, **kwargs)
            except usb.core.USBError as exception:
                self._handle_exception(message_template, exception)
        return wrapper
    return outer


class USBDevice:
    """Provide an interface to a connected USB device."""

    INTERFACE = 0
    IN_ENDPOINT = 0

    def __init__(self, raw_device):
        """Initialize the device given a pyusb device."""
        self.raw_device = raw_device
        self._endpoint = None

    def connect(self):
        """Connect to the usb device.

        Detach the kernel driver if it is attached and then claim
        the interface. This must be done before calling any of the other
        methods of this class. Changes to the INTERFACE and IN_ENDPOINT
        attributes after this point are not supported.
        """
        self._detach_kernel_driver_if_attached()
        self._set_configuration()
        self._claim_interface()
        self._endpoint = self._get_endpoint()

    def is_input(self):
        """Return if the device is an input."""
        endpoint_address = self._endpoint.bEndpointAddress
        direction = usb.util.endpoint_direction(endpoint_address)
        return direction == usb.util.ENDPOINT_IN

    def is_output(self):
        """Return if the device is an output."""
        return not self.is_input()

    def flush(self):
        """Flush the input buffer."""
        try:
            while self._endpoint.read(1):
                pass
        except usb.core.USBError:
            pass

    def read(self, number_of_bytes):
        """Read a number of bytes from the device.

        If there is no data to be read an empty bytes object is
        returned. The 'number_of_bytes' arguments gives the maximum
        number of bytes to read. The function will block untill that
        number of bytes has been received.
        """
        return self._read_blocking(number_of_bytes)

    def write(self, data):
        """Write the given bytes to the device.

        Return the number of bytes written. An exception is raised if
        not all data could be written.
        """
        try:
            bytes_written = self._endpoint.write(data)
            if bytes_written != len(data):
                self._handle_incomplete_write(bytes_written, data)
            return bytes_written
        except usb.core.USBError as exception:
            self._handle_write_exception(exception)

    @property
    def class_identifier(self):
        """Return a unique identifier for the device class."""
        return DeviceClassID(vendor_id=self.raw_device.idVendor,
                             product_id=self.raw_device.idProduct,
                             release_number=self.raw_device.bcdDevice)

    def device_info(self):
        """Return a string containing device information."""
        return repr(self.raw_device)

    def _read_blocking(self, number_of_bytes):
        data = b''
        while len(data) < number_of_bytes:
            bytes_remaining = number_of_bytes - len(data)
            data += self._read_non_blocking(bytes_remaining)
        return data

    def _read_non_blocking(self, number_of_bytes):
        try:
            return bytes(self._endpoint.read(number_of_bytes))
        except usb.core.USBError:
            return b''

    def _handle_incomplete_write(self, bytes_written, data):
        msg = 'Not all data written to interface {} of device {}.'.format(
            self.INTERFACE, self.device_info())
        msg2 = 'Tried to write {} bytes ({}), but only wrote {}.'.format(
            len(data), data, bytes_written)
        _LOGGER.error(msg)
        _LOGGER.error(msg2)
        raise IncompleteUSBWrite(msg)

    def _handle_write_exception(self, exception):
        msg = 'Error when writing to interface {} of device {}: {}'.format(
            self.INTERFACE, self.device_info(), str(exception))
        _LOGGER.error(msg)
        raise USBError(msg) from exception

    def _detach_kernel_driver_if_attached(self):
        if self._is_kernel_driver_attached():
            self._detach_kernel_driver()

    def _is_kernel_driver_attached(self):
        return self.raw_device.is_kernel_driver_active(self.INTERFACE)

    @_managed('detaching kernel driver for interface {interface} of ' +
              'device {device}')
    def _detach_kernel_driver(self):
        self.raw_device.detach_kernel_driver(self.INTERFACE)

    @_managed('setting configuration for device {device}')
    def _set_configuration(self):
        self.raw_device.set_configuration()

    @_managed('claiming interface {interface} of device {device}')
    def _claim_interface(self):
        usb.util.claim_interface(self.raw_device, self.INTERFACE)

    def _get_endpoint(self):
        active_configuration = self.raw_device.get_active_configuration()
        interface = active_configuration.interfaces()[self.INTERFACE]
        return interface.endpoints()[self.IN_ENDPOINT]

    def _format_message(self, template, **kwargs):
        return template.format(interface=self.INTERFACE,
                               device=self.device_info(), **kwargs)

    def _handle_exception(self, template, exception):
        error_template = 'Error ' + template + ':\n{exception}'
        msg = self._format_message(error_template, exception=str(exception))
        _LOGGER.error(msg)
        raise USBError(msg) from exception
