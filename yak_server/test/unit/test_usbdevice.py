#! /usr/bin/env python3

# pylint: disable = no-self-use, unused-argument

import array
import logging
import unittest
import unittest.mock
import usb

import test.util # noqa

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


class StubUSBRead():
    data = [None, None, None] + [ord('a') + i for i in range(26)]

    def __init__(self):
        self.count = 0

    def __call__(self, number_of_bytes):
        start = self.count
        end = start + min(number_of_bytes, 2)
        packet = self._make_packet(start, end)
        self.count += len(packet) or 1
        if not packet:
            raise usb.USBError('')
        return array.array('B', packet)

    def _make_packet(self, start, end):
        packet = []
        for byte in self.data[start:end]:
            if byte is None:
                break
            packet.append(byte)
        return packet


class TestUSBDevice(test.util.TestCase):
    def setUp(self):
        self.search_parameters = {'vendor_id': 1337,
                                  'product_id': 42,
                                  'device_release_number': 3}
        self.expected_raw_device = {'idVendor': 1337,
                                    'idProduct': 42,
                                    'bcdDevice': 3}
        logging.getLogger('yak_server.usbdevice').setLevel(100)
        self.usb_util_patch = self.start_patch('yak_server.usbdevice.usb.util')
        self.mock_usb_util = self.usb_util_patch.mock
        self.usb_device_mocks = self._make_usb_device_mocks()

    @patch_usb_find()
    def test_find_usb_device(self, usb_find_mock):
        usb_devices = list(yak_server.usbdevice.find(**self.search_parameters))
        usb_find_mock.assert_called_once_with(**self.expected_raw_device,
                                              find_all=True)
        self.assertEqual(len(usb_devices), 1)
        self.assertEqual(usb_devices[0].raw_device, self.expected_raw_device)

    @patch_usb_find(match_count=2)
    def test_find_usb_device_logs_parameters_and_results(self, usb_find_mock):
        with self.assertLogs('yak_server.usbdevice', level='DEBUG') as logs:
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

    def test_connect_detaches_driver_and_claims_interface(self):
        manager_mock = unittest.mock.MagicMock()
        mock_raw_device = manager_mock.raw_device
        self.mock_usb_util.claim_interface = manager_mock.claim_interface
        usb_device = yak_server.usbdevice.USBDevice(mock_raw_device)
        usb_device.connect()

        mock_call = unittest.mock.call
        expected_calls = [mock_call.raw_device.detach_kernel_driver(0),
                          mock_call.claim_interface(manager_mock.raw_device, 0)
                         ]
        manager_mock.assert_has_calls(expected_calls)

    def test_log_detaching_kernel_driver(self):
        mock_raw_device = unittest.mock.MagicMock()
        with self.assertLogs('yak_server.usbdevice', level='DEBUG') as logs:
            usb_device = yak_server.usbdevice.USBDevice(mock_raw_device)
            usb_device.connect()

            log_output = '\n'.join(logs.output)
            self.assertIn('detaching', log_output.lower())

    def test_connect_succeeds_when_no_kernel_driver_attached(self):
        mock_raw_device = unittest.mock.MagicMock()
        mock_raw_device.is_kernel_driver_active.return_value = False
        usb_device = yak_server.usbdevice.USBDevice(mock_raw_device)
        usb_device.connect()

    def test_connect_raises_exception_when_unable_to_detach_driver(self):
        mock_raw_device = unittest.mock.MagicMock()
        mock_raw_device.detach_kernel_driver.side_effect = usb.USBError('')
        mock_raw_device.is_kernel_driver_active.return_value = True
        usb_device = yak_server.usbdevice.USBDevice(mock_raw_device)

        with self.assertRaises(yak_server.usbdevice.USBError):
            usb_device.connect()

    def test_connect_logs_error_when_unable_to_detach_kernel_driver(self):
        mock_raw_device = unittest.mock.Mock()
        mock_raw_device.detach_kernel_driver.side_effect = usb.USBError('')
        mock_raw_device.is_kernel_driver_active.return_value = True
        usb_device = yak_server.usbdevice.USBDevice(mock_raw_device)

        with self.assertLogs(logger='yak_server.usbdevice',
                             level='ERROR') as logs:
            try:
                usb_device.connect()
            except yak_server.usbdevice.USBError:
                pass

    def test_log_claim_interface(self):
        mock_raw_device = unittest.mock.MagicMock()
        with self.assertLogs('yak_server.usbdevice', level='DEBUG') as logs:
            usb_device = yak_server.usbdevice.USBDevice(mock_raw_device)
            usb_device.connect()

            log_output = '\n'.join(logs.output)
            self.assertIn('claim', log_output.lower())
            self.assertIn('interface', log_output.lower())

    def test_connect_raises_exception_when_unable_to_claim_interface(self):
        self.mock_usb_util.claim_interface.side_effect = usb.USBError('')
        mock_raw_device = unittest.mock.Mock()
        usb_device = yak_server.usbdevice.USBDevice(mock_raw_device)

        with self.assertRaises(yak_server.usbdevice.USBError):
            usb_device.connect()

    def test_connect_logs_when_unable_to_claim_interface(self):
        self.mock_usb_util.claim_interface.side_effect = usb.USBError('')
        mock_raw_device = unittest.mock.Mock()
        usb_device = yak_server.usbdevice.USBDevice(mock_raw_device)

        with self.assertLogs('yak_server.usbdevice', level='ERROR') as logs:
            try:
                usb_device.connect()
            except yak_server.usbdevice.USBError:
                pass

    def test_is_input_returns_true_for_in_endpoint(self):
        endpoint_direction_mock = self.mock_usb_util.endpoint_direction
        endpoint_direction_mock.return_value = usb.util.ENDPOINT_IN
        endpoint_address = self.usb_device_mocks.endpoint.bEndpointAddress
        usb_device = self._make_usb_device()

        usb_device.connect()

        self.assertTrue(usb_device.is_input())
        endpoint_direction_mock.assert_called_with(endpoint_address)

    def test_is_input_returns_false_for_out_endpoint(self):
        endpoint_direction_mock = self.mock_usb_util.endpoint_direction
        endpoint_direction_mock.return_value = usb.util.ENDPOINT_OUT
        endpoint_address = self.usb_device_mocks.endpoint.bEndpointAddress
        usb_device = self._make_usb_device()

        usb_device.connect()

        self.assertFalse(usb_device.is_input())
        endpoint_direction_mock.assert_called_with(endpoint_address)

    def test_is_output_returns_true_for_out_endpoint(self):
        endpoint_direction_mock = self.mock_usb_util.endpoint_direction
        endpoint_direction_mock.return_value = usb.util.ENDPOINT_OUT
        endpoint_address = self.usb_device_mocks.endpoint.bEndpointAddress
        usb_device = self._make_usb_device()

        usb_device.connect()

        self.assertTrue(usb_device.is_output())
        endpoint_direction_mock.assert_called_with(endpoint_address)

    def test_is_output_returns_false_for_in_endpoint(self):
        endpoint_direction_mock = self.mock_usb_util.endpoint_direction
        endpoint_direction_mock.return_value = usb.util.ENDPOINT_IN
        endpoint_address = self.usb_device_mocks.endpoint.bEndpointAddress
        usb_device = self._make_usb_device()

        usb_device.connect()

        self.assertFalse(usb_device.is_output())
        endpoint_direction_mock.assert_called_with(endpoint_address)

    def test_flush_input_device(self):
        read_stub = StubUSBRead()
        read_stub.data = [ord('a'), ord('b'), None, ord('c'), ord('d')]
        self.usb_device_mocks.endpoint.read.side_effect = read_stub
        usb_device = self._make_usb_device()
        usb_device.connect()

        usb_device.flush()
        data = usb_device.read(2)

        self.assertEqual(data, b'cd')

    def test_read(self):
        stub_data = array.array('B', b'1234')
        self.usb_device_mocks.endpoint.read.return_value = stub_data
        usb_device = self._make_usb_device()
        usb_device.connect()

        data = usb_device.read(4)

        self.usb_device_mocks.endpoint.read.assert_called_with(4)
        self.assertEqual(data, b'1234')

    def test_read_with_split_data(self):
        self.usb_device_mocks.endpoint.read.side_effect = StubUSBRead()
        usb_device = self._make_usb_device()
        usb_device.connect()

        data = usb_device.read(4)

        self.assertEqual(data, b'abcd')

    def test_read_with_split_and_extra_data(self):
        self.usb_device_mocks.endpoint.read.side_effect = StubUSBRead()
        usb_device = self._make_usb_device()
        usb_device.connect()

        data = usb_device.read(5)

        self.assertEqual(data, b'abcde')

    def test_write(self):
        usb_device = self._make_usb_device()
        self.usb_device_mocks.endpoint.write.return_value = 4
        usb_device.connect()

        number_of_bytes_written = usb_device.write(b'test')

        self.usb_device_mocks.endpoint.write.assert_called_with(b'test')
        self.assertEqual(number_of_bytes_written, 4)

    def test_write_raises_exception_on_error(self):
        usb_device = self._make_usb_device()
        self.usb_device_mocks.endpoint.write.side_effect = usb.USBError('')
        usb_device.connect()

        with self.assertRaises(yak_server.usbdevice.USBError):
            usb_device.write(b'test')

    def test_write_raises_exception_on_incomplete_write(self):
        usb_device = self._make_usb_device()
        self.usb_device_mocks.endpoint.write.return_value = 2
        usb_device.connect()

        with self.assertRaises(yak_server.usbdevice.IncompleteUSBWrite):
            usb_device.write(b'test')

    def test_write_logs_error(self):
        usb_device = self._make_usb_device()
        self.usb_device_mocks.endpoint.write.side_effect = usb.USBError('')
        usb_device.connect()

        with self.assertLogs('yak_server.usbdevice', level='ERROR') as logs:
            try:
                usb_device.write(b'test')
            except yak_server.usbdevice.USBError:
                pass

    def _make_usb_device(self):
        return yak_server.usbdevice.USBDevice(self.usb_device_mocks.raw_device)

    def _make_usb_device_mocks(self):
        usb_device_mocks = unittest.mock.Mock()
        usb_device_mocks.raw_device = unittest.mock.Mock()
        usb_device_mocks.config = unittest.mock.Mock()
        usb_device_mocks.interface = unittest.mock.Mock()
        usb_device_mocks.endpoint = unittest.mock.Mock()

        raw_device_mock = usb_device_mocks.raw_device
        get_active_config_mock = raw_device_mock.get_active_configuration
        get_active_config_mock.return_value = usb_device_mocks.config
        interfaces_mock = usb_device_mocks.config.interfaces
        interfaces_mock.return_value = (usb_device_mocks.interface, )
        endpoints_mock = usb_device_mocks.interface.endpoints
        endpoints_mock.return_value = (usb_device_mocks.endpoint, )
        return usb_device_mocks
