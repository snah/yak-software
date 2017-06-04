import logging
import usb

_logger = logging.getLogger(__name__)

class USBError(Exception):
    """General USB exception."""

def _translate_search_parameters(search_parameters):
    """Translate search parameters into kwargs for pyusb."""
    parameter_translation_table = {'product_id': 'idProduct',
                                   'vendor_id': 'idVendor',
                                   'device_release_number': 'bcdDevice'}

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
    product_id, vendor_id and device_release_number, all of which
    expect an integer value.
    """
    _logger.info('Scanning for usb devices with %s', search_parameters)

    find_kwargs = _translate_search_parameters(search_parameters)
    raw_devices = usb.core.find(**find_kwargs, find_all=True)

    for raw_device in raw_devices:
        _logger.info('Found usb device: %s', repr(raw_device))

    return (USBDevice(raw_device) for raw_device in raw_devices )
    

class USBDevice:
    """Provide an interface to a connected USB device."""
    INTERFACE = 0
    ENDPOINT = 0

    def __init__(self, raw_device):
        self.raw_device = raw_device

    def connect(self):
        """Connect to the usb device.
        
        Detach the kernel driver if it is attached and then claim
        the interface.
        """
        self._detach_kernel_driver()
        self._claim_interface()

    def is_input(self):
        endpoint = self._get_endpoint()
        direction = usb.util.endpoint_direction(endpoint.bEndpointAddress)
        return direction == usb.util.ENDPOINT_IN

    def is_output(self):
        return not self.is_input()

    def read(self, number_of_bytes):
        """Read a number of bytes from the device."""
        endpoint = self._get_endpoint()
        endpoint.read(number_of_bytes)

    def _detach_kernel_driver(self):
        if self.raw_device.is_kernel_driver_active():
            _logger.info('Detaching kernel driver from device %s', repr(self.raw_device))
            try:
                self.raw_device.detach_kernel_driver(self.INTERFACE)
            except usb.USBError as e:
                _logger.error('Error detaching kernel driver for interface %s:\n%s',
                              self.raw_device, str(e))
                raise USBError from e

    def _claim_interface(self):
        usb.util.claim_interface(self.raw_device, self.INTERFACE)

    def _get_endpoint(self):
        active_configuration = self.raw_device.get_active_configuration()
        interface = active_configuration.interfaces()[self.INTERFACE]
        return interface.endpoints()[self.ENDPOINT]
