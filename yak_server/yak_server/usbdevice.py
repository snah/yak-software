import usb

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
    find_kwargs = _translate_search_parameters(search_parameters)
    raw_devices = usb.core.find(**find_kwargs)
    return (USBDevice(raw_device) for raw_device in raw_devices )
    


class USBDevice:
    """Provide an interface to a connected USB device."""
    def __init__(self, raw_device):
        self.raw_device = raw_device
