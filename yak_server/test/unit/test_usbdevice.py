import functools
import logging
import unittest
import unittest.mock

import test.util

import yak_server.usbdevice

import usb


def mock_usb_find(match_count=1):
    def fake_find_function(**kwargs):
        del kwargs['find_all']
        return [kwargs] * match_count
    mock = unittest.mock.Mock(side_effect = fake_find_function)
    callable_mock = lambda: mock
    return unittest.mock.patch('usb.core.find', new_callable=callable_mock)


class TestUSBDevice(test.util.TestCase):
    def setUp(self):
        self.search_parameters = {'vendor_id': 1337,
                                  'product_id': 42,
                                  'device_release_number': 3}
        self.expected_raw_device = {'idVendor': 1337,
                                      'idProduct': 42,
                                      'bcdDevice': 3}
        logging.getLogger('yak_server.usbdevice').setLevel(100)
        self.mock_usb_util = self.start_patch('yak_server.__main__.usb.util').mock
        self.usb_device_mocks = self._make_usb_device_mocks()

    @mock_usb_find()
    def test_find_usb_device(self, usb_find_mock):
        usb_devices = list(yak_server.usbdevice.find(**self.search_parameters))
        usb_find_mock.assert_called_once_with(**self.expected_raw_device, find_all=True)
        self.assertEqual(len(usb_devices), 1)
        self.assertEqual(usb_devices[0].raw_device, self.expected_raw_device)

    @mock_usb_find(match_count=2)
    def test_find_usb_device_logs_parameters_and_results(self, usb_find_mock):
        with self.assertLogs('yak_server.usbdevice', level='DEBUG') as logs:
            yak_server.usbdevice.find(**self.search_parameters)

            log_output = '\n'.join(logs.output)
            self.assertIn(str(self.search_parameters), log_output)
            self.assertEqual(log_output.count('Found usb device'), 2,
                    msg='Did not print info on the correct number of usb devices')

    @mock_usb_find()
    def test_find_usb_device_with_not_all_parameters(self, usb_find_mock):
        del self.search_parameters['product_id']
        del self.expected_raw_device['idProduct']

        usb_devices = list(yak_server.usbdevice.find(**self.search_parameters))

        self.assertEqual(len(usb_devices), 1)
        self.assertEqual(usb_devices[0].raw_device, self.expected_raw_device)

    @mock_usb_find(match_count=3)
    def test_find_usb_device_multiple_matches(self, mock_usb_find):
        usb_devices = list(yak_server.usbdevice.find(**self.search_parameters))

        self.assertEqual(len(usb_devices), 3)
        self.assertEqual(usb_devices[0].raw_device, self.expected_raw_device)
        self.assertEqual(usb_devices[1].raw_device, self.expected_raw_device)
        self.assertEqual(usb_devices[2].raw_device, self.expected_raw_device)

    @mock_usb_find(match_count=0)
    def test_find_usb_device_multiple_matches(self, mock_usb_find):
        usb_devices = list(yak_server.usbdevice.find())

        self.assertEqual(usb_devices, [])

    def test_connect_detaches_driver_and_claims_interface(self):
        manager_mock = unittest.mock.MagicMock()
        mock_raw_device = manager_mock.raw_device
        self.mock_usb_util.claim_interface = manager_mock.claim_interface
        usb_device = yak_server.usbdevice.USBDevice(mock_raw_device)
        usb_device.connect()

        expected_calls = [unittest.mock.call.raw_device.detach_kernel_driver(0),
                          unittest.mock.call.claim_interface(manager_mock.raw_device, 0)]
        manager_mock.assert_has_calls(expected_calls)

    def test_log_detaching_kernel_driver(self):
        mock_raw_device = unittest.mock.MagicMock()
        with self.assertLogs('yak_server.usbdevice', level='DEBUG') as logs:
            usb_device = yak_server.usbdevice.USBDevice(mock_raw_device)
            usb_device.connect()

            log_output = '\n'.join(logs.output)
            self.assertIn('detaching', log_output.lower())

    def test_connect_succeeds_if_no_kernel_driver_attached(self):
        mock_raw_device = unittest.mock.MagicMock()
        mock_raw_device.is_kernel_driver_active.return_value = False
        usb_device = yak_server.usbdevice.USBDevice(mock_raw_device)
        usb_device.connect()

    def test_connect_raises_exception_if_unable_to_detach_kernel_driver(self):
        mock_raw_device = unittest.mock.MagicMock()
        mock_raw_device.detach_kernel_driver.side_effect = usb.USBError('')
        mock_raw_device.is_kernel_driver_active.return_value = True
        usb_device = yak_server.usbdevice.USBDevice(mock_raw_device)

        with self.assertRaises(yak_server.usbdevice.USBError):
            usb_device.connect()

    def test_connect_logs_error_if_unable_to_detach_kernel_driver(self):
        mock_raw_device = unittest.mock.Mock()
        mock_raw_device.detach_kernel_driver.side_effect = usb.USBError('')
        mock_raw_device.is_kernel_driver_active.return_value = True
        usb_device = yak_server.usbdevice.USBDevice(mock_raw_device)

        with self.assertLogs(logger='yak_server.usbdevice', level='ERROR') as logs:
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

    def test_connect_raises_exception_if_unable_to_claim_interface(self):
        self.mock_usb_util.claim_interface.side_effect = usb.USBError('')
        mock_raw_device = unittest.mock.Mock()
        usb_device = yak_server.usbdevice.USBDevice(mock_raw_device)

        with self.assertRaises(yak_server.usbdevice.USBError):
            usb_device.connect()

    def test_connect_raises_exception_if_unable_to_claim_interface(self):
        self.mock_usb_util.claim_interface.side_effect = usb.USBError('')
        mock_raw_device = unittest.mock.Mock()
        usb_device = yak_server.usbdevice.USBDevice(mock_raw_device)

        with self.assertLogs('yak_server.usbdevice', level='ERROR') as logs:
            try:
                usb_device.connect()
            except yak_server.usbdevice.USBError:
                pass


    def test_is_input_returns_true_for_in_endpoint(self):
        self.mock_usb_util.endpoint_direction.return_value = usb.util.ENDPOINT_IN
        endpoint_address = self.usb_device_mocks.endpoint.bEndpointAddress
        usb_device = yak_server.usbdevice.USBDevice(self.usb_device_mocks.raw_device)
        usb_device.connect()
        
        self.assertTrue(usb_device.is_input())
        self.mock_usb_util.endpoint_direction.assert_called_with(endpoint_address)

    def test_is_input_returns_false_for_out_endpoint(self):
        self.mock_usb_util.endpoint_direction.return_value = usb.util.ENDPOINT_OUT
        endpoint_address = self.usb_device_mocks.endpoint.bEndpointAddress
        usb_device = yak_server.usbdevice.USBDevice(self.usb_device_mocks.raw_device)
        usb_device.connect()
        
        self.assertFalse(usb_device.is_input())
        self.mock_usb_util.endpoint_direction.assert_called_with(endpoint_address)

    def test_is_output_returns_true_for_out_endpoint(self):
        self.mock_usb_util.endpoint_direction.return_value = usb.util.ENDPOINT_OUT
        endpoint_address = self.usb_device_mocks.endpoint.bEndpointAddress
        usb_device = yak_server.usbdevice.USBDevice(self.usb_device_mocks.raw_device)
        usb_device.connect()
        
        self.assertTrue(usb_device.is_output())
        self.mock_usb_util.endpoint_direction.assert_called_with(endpoint_address)

    def test_is_output_returns_false_for_in_endpoint(self):
        self.mock_usb_util.endpoint_direction.return_value = usb.util.ENDPOINT_IN
        endpoint_address = self.usb_device_mocks.endpoint.bEndpointAddress
        usb_device = yak_server.usbdevice.USBDevice(self.usb_device_mocks.raw_device)
        usb_device.connect()
        
        self.assertFalse(usb_device.is_output())
        self.mock_usb_util.endpoint_direction.assert_called_with(endpoint_address)

    def test_read(self):
        device = yak_server.usbdevice.USBDevice(self.usb_device_mocks.raw_device)
        device.connect()

        data = device.read(4)

        self.usb_device_mocks.endpoint.read.assert_called_with(4)
        self.assertEqual(data, self.usb_device_mocks.endpoint.read())

    def test_read_returns_empty_bytes_object_on_timout(self):
        self.usb_device_mocks.endpoint.read.side_effect = usb.USBError('')
        device = yak_server.usbdevice.USBDevice(self.usb_device_mocks.raw_device)
        device.connect()

        data = device.read(4)

        self.assertEqual(data, b'')

    def _make_usb_device_mocks(self):
        usb_device_mocks = unittest.mock.Mock()
        usb_device_mocks.raw_device = unittest.mock.Mock()
        usb_device_mocks.config = unittest.mock.Mock()
        usb_device_mocks.interface = unittest.mock.Mock()
        usb_device_mocks.endpoint = unittest.mock.Mock()

        usb_device_mocks.raw_device.get_active_configuration.return_value = usb_device_mocks.config
        usb_device_mocks.config.interfaces.return_value = (usb_device_mocks.interface, )
        usb_device_mocks.interface.endpoints.return_value = (usb_device_mocks.endpoint, )
        return usb_device_mocks
