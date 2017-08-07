#! /usr/bin/env python3

# pylint: disable = no-self-use, unused-argument

import logging
import unittest
import unittest.mock
import usb

import test.util # noqa
from test.doubles import fake_usb # noqa

import yak_server.usbdevice


def patch_usb_find(match_count=1):
    """Patch the usb.core.find function."""
    def fake_find_function(**kwargs):
        del kwargs['find_all']
        return [kwargs] * match_count
    mock = unittest.mock.Mock(side_effect=fake_find_function)

    def callable_mock():
        return mock
    return unittest.mock.patch('usb.core.find', new_callable=callable_mock)


class TestUSBDevice(test.util.TestCase):
    LOGGER = 'yak_server.usbdevice'

    def setUp(self):
        self.search_parameters = {'vendor_id': 1337,
                                  'product_id': 42,
                                  'device_release_number': 3}
        self.expected_raw_device = {'idVendor': 1337,
                                    'idProduct': 42,
                                    'bcdDevice': 3}
        logging.getLogger('yak_server.usbdevice').setLevel(100)

    @patch_usb_find()
    def test_find_usb_device(self, usb_find_mock):
        usb_devices = list(yak_server.usbdevice.find(**self.search_parameters))
        usb_find_mock.assert_called_once_with(**self.expected_raw_device,
                                              find_all=True)
        self.assertEqual(len(usb_devices), 1)
        self.assertEqual(usb_devices[0].raw_device, self.expected_raw_device)

    @patch_usb_find(match_count=2)
    def test_find_usb_device_logs_parameters_and_results(self, usb_find_mock):
        with self.assertLogs(self.LOGGER, level='DEBUG') as logs:
            yak_server.usbdevice.find(**self.search_parameters)

            log_output = '\n'.join(logs.output)
            self.assertIn(str(self.search_parameters), log_output)
            self.assertEqual(log_output.count('Found usb device'), 2,
                             msg='Should print info for 2 usb devices')

    @patch_usb_find()
    def test_find_usb_device_with_not_all_parameters(self, usb_find_mock):
        del self.search_parameters['product_id']
        del self.expected_raw_device['idProduct']

        usb_devices = list(yak_server.usbdevice.find(**self.search_parameters))

        self.assertEqual(len(usb_devices), 1)
        self.assertEqual(usb_devices[0].raw_device, self.expected_raw_device)

    @patch_usb_find(match_count=3)
    def test_find_usb_device_multiple_matches(self, usb_find_mock):
        usb_devices = list(yak_server.usbdevice.find(**self.search_parameters))

        self.assertEqual(len(usb_devices), 3)
        self.assertEqual(usb_devices[0].raw_device, self.expected_raw_device)
        self.assertEqual(usb_devices[1].raw_device, self.expected_raw_device)
        self.assertEqual(usb_devices[2].raw_device, self.expected_raw_device)

    @patch_usb_find(match_count=0)
    def test_find_usb_device_no_matches(self, usb_find_mock):
        usb_devices = list(yak_server.usbdevice.find())

        self.assertEqual(usb_devices, [])

    def test_connect_detaches_kernel_driver(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)

        usb_device.connect()

        self.assertIn(usb_device.INTERFACE,
                      fake_raw_device.detached_kernel_drivers)

    def test_log_detaching_kernel_driver(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        with self.assertLogs(self.LOGGER, level='DEBUG') as logs:
            usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)
            usb_device.connect()

            log_output = '\n'.join(logs.output)
            self.assertIn('detaching', log_output.lower())

    def test_connect_succeeds_when_no_kernel_driver_attached(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)
        fake_raw_device.detached_kernel_drivers.add(usb_device.INTERFACE)

        usb_device.connect()

        self.assertIn(usb_device.INTERFACE,
                      fake_raw_device.detached_kernel_drivers)

    def test_connect_raises_exception_when_unable_to_detach_driver(self):
        stub_raw_device = unittest.mock.Mock()
        stub_raw_device.is_kernel_driver_active.return_value = True
        stub_raw_device.detach_kernel_driver.side_effect = usb.USBError('')
        usb_device = yak_server.usbdevice.USBDevice(stub_raw_device)

        with self.assertRaises(yak_server.usbdevice.USBError):
            usb_device.connect()

    def test_connect_logs_error_when_unable_to_detach_kernel_driver(self):
        stub_raw_device = unittest.mock.Mock()
        stub_raw_device.is_kernel_driver_active.return_value = True
        stub_raw_device.detach_kernel_driver.side_effect = usb.USBError('')
        usb_device = yak_server.usbdevice.USBDevice(stub_raw_device)

        with self.assertLogs(logger=self.LOGGER, level='ERROR') as logs:
            try:
                usb_device.connect()
            except yak_server.usbdevice.USBError:
                pass

    def test_connect_sets_configuration(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)

        usb_device.connect()

        self.assertEqual(fake_raw_device.configuration_number, 0)

    def test_connect_raises_exception_when_unable_to_set_configuration(self):
        stub_raw_device = unittest.mock.Mock()
        stub_raw_device.is_kernel_driver_active.return_value = True
        stub_raw_device.set_configuration.side_effect = usb.USBError('')
        usb_device = yak_server.usbdevice.USBDevice(stub_raw_device)

        with self.assertRaises(yak_server.usbdevice.USBError):
            usb_device.connect()

    def test_connect_logs_when_unable_to_set_configuration(self):
        stub_raw_device = unittest.mock.Mock()
        stub_raw_device.is_kernel_driver_active.return_value = True
        stub_raw_device.set_configuration.side_effect = usb.USBError('')
        usb_device = yak_server.usbdevice.USBDevice(stub_raw_device)

        with self.assertLogs(logger=self.LOGGER,
                             level='ERROR') as logs:
            try:
                usb_device.connect()
            except yak_server.usbdevice.USBError:
                pass

    def test_connect_claims_interface(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)

        usb_device.connect()

        self.assertIn(usb_device.INTERFACE, fake_raw_device.claimed_interfaces)

    def test_connect_logs_claim_interface(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        with self.assertLogs('yak_server.usbdevice', level='DEBUG') as logs:
            usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)
            usb_device.connect()

            log_output = '\n'.join(logs.output)
            self.assertIn('claim', log_output.lower())
            self.assertIn('interface', log_output.lower())

    def test_connect_raises_exception_when_unable_to_claim_interface(self):
        self.start_patch('yak_server.usbdevice.usb.util.claim_interface',
                         side_effect=usb.USBError(''))
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)

        with self.assertRaises(yak_server.usbdevice.USBError):
            usb_device.connect()

    def test_connect_logs_when_unable_to_claim_interface(self):
        self.start_patch('yak_server.usbdevice.usb.util.claim_interface',
                         side_effect=usb.USBError(''))
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)

        with self.assertLogs('yak_server.usbdevice', level='ERROR') as logs:
            try:
                usb_device.connect()
            except yak_server.usbdevice.USBError:
                pass

    def test_is_input_returns_true_for_in_endpoint(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)

        usb_device.connect()

        self.assertTrue(usb_device.is_input())

    def test_is_input_returns_false_for_out_endpoint(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        interface = fake_raw_device.configuration.interface
        interface.endpoint_list = [interface.out_endpoint]
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)

        usb_device.connect()

        self.assertFalse(usb_device.is_input())

    def test_is_output_returns_true_for_out_endpoint(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        interface = fake_raw_device.configuration.interface
        interface.endpoint_list = [interface.out_endpoint]
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)

        usb_device.connect()

        self.assertTrue(usb_device.is_output())

    def test_is_output_returns_false_for_in_endpoint(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)

        usb_device.connect()

        self.assertFalse(usb_device.is_output())

    def test_flush_input_device(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        endpoint = fake_raw_device.configuration.interface.in_endpoint
        endpoint.read_data = [ord('a'), ord('b'), None, ord('c'), ord('d')]
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)
        usb_device.connect()

        usb_device.flush()
        data = usb_device.read(2)

        self.assertEqual(data, b'cd')

    def test_read(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)
        usb_device.connect()

        data = usb_device.read(2)

        self.assertEqual(data, b'ab')

    def test_read_with_split_data(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        endpoint = fake_raw_device.configuration.interface.in_endpoint
        endpoint.read_data = [ord('a'), ord('b'), None, ord('c'), ord('d')]
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)
        usb_device.connect()

        data = usb_device.read(4)

        self.assertEqual(data, b'abcd')

    def test_read_with_split_and_extra_data(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        endpoint = fake_raw_device.configuration.interface.in_endpoint
        endpoint.read_data = [ord('a'), ord('b'), None, ord('c'), ord('d')]
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)
        usb_device.connect()

        data = usb_device.read(3)

        self.assertEqual(data, b'abc')

    def test_write(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        interface = fake_raw_device.configuration.interface
        interface.endpoint_list = [interface.out_endpoint]
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)
        usb_device.connect()

        number_of_bytes_written = usb_device.write(b'test')

        self.assertEqual(number_of_bytes_written, 4)

    def test_write_raises_exception_on_error(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        stub_endpoint = unittest.mock.Mock()
        stub_endpoint.write.side_effect = usb.USBError('')
        fake_raw_device.configuration.interface.endpoint_list = [stub_endpoint]
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)
        usb_device.connect()

        with self.assertRaises(yak_server.usbdevice.USBError):
            usb_device.write(b'test')

    def test_write_raises_exception_on_incomplete_write(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        stub_endpoint = unittest.mock.Mock()
        stub_endpoint.write.return_value = 2
        fake_raw_device.configuration.interface.endpoint_list = [stub_endpoint]
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)
        usb_device.connect()

        with self.assertRaises(yak_server.usbdevice.IncompleteUSBWrite):
            usb_device.write(b'test')

    def test_write_logs_error(self):
        fake_raw_device = fake_usb.FakeRawUSBDevice()
        stub_endpoint = unittest.mock.Mock()
        stub_endpoint.write.side_effect = usb.USBError('')
        fake_raw_device.configuration.interface.endpoint_list = [stub_endpoint]
        usb_device = yak_server.usbdevice.USBDevice(fake_raw_device)
        usb_device.connect()

        with self.assertLogs('yak_server.usbdevice', level='ERROR') as logs:
            try:
                usb_device.write(b'test')
            except yak_server.usbdevice.USBError:
                pass
