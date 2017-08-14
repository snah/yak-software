# pylint: disable = no-self-use, unused-argument

import array
import usb


class FakeRawUSBDevice:
    def __init__(self):
        self.detached_kernel_drivers = set()
        self.claimed_interfaces = set()
        self.configuration_number = None
        self.configuration = FakeUSBConfiguration()
        self._ctx = FakeUSBContext()

    def is_kernel_driver_active(self, interface_number):
        return interface_number not in self.detached_kernel_drivers

    def detach_kernel_driver(self, interface_number):
        if interface_number in self.detached_kernel_drivers:
            raise usb.core.USBError('No kernel driver active.')
        self.detached_kernel_drivers.add(interface_number)

    def get_active_configuration(self):
        if self.configuration_number is None:
            raise AssertionError('You should set the configuration first.')
        return self.configuration

    def set_configuration(self, configuration=0):
        self.configuration_number = configuration


class FakeUSBConfiguration:
    def __init__(self):
        self.interface = FakeUSBInterface()

    def interfaces(self):
        return [self.interface]


class FakeUSBInterface:
    def __init__(self):
        self.in_endpoint = FakeUSBInEndpoint()
        self.out_endpoint = FakeUSBOutEndpoint()
        self.endpoint_list = [self.in_endpoint, self.out_endpoint]

    def endpoints(self):
        return self.endpoint_list


class FakeUSBInEndpoint:
    read_data = [None, None, None] + [ord('a') + i for i in range(26)]

    def __init__(self):
        self.bEndpointAddress = 0x80 # noqa
        self.read_count = 0

    def read(self, number_of_bytes):
        start = self.read_count
        end = start + min(number_of_bytes, 2)
        packet = self._make_packet(start, end)
        self.read_count += len(packet) or 1
        if not packet:
            raise usb.USBError('')
        return array.array('B', packet)

    def _make_packet(self, start, end):
        packet = []
        for byte in self.read_data[start:end]:
            if byte is None:
                break
            packet.append(byte)
        return packet


class FakeUSBOutEndpoint:
    def __init__(self):
        self.bEndpointAddress = 0x00 #noqa

    def write(self, data):
        return len(data)


class FakeUSBContext:
    def managed_claim_interface(self, device, interface_number):
        if device.is_kernel_driver_active(interface_number):
            msg = 'Kernel driver should be detached before claiming interface.'
            raise AssertionError(msg)
        if device.configuration_number is None:
            raise AssertionError('You should set the configuration first.')
        device.claimed_interfaces.add(interface_number)
