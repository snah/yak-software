import functools
import unittest
import unittest.mock

import test.util

import yak_server.usbdevice

import usb


def mock_usb_find(match_count=1):
    def fake_find_function(**kwargs):
        return [kwargs] * match_count
    callable_mock = lambda: fake_find_function
    return unittest.mock.patch('usb.core.find', new_callable=callable_mock)


class TestUSBDevice(test.util.TestCase):
    @mock_usb_find()
    def test_find_usb_device(self, usb_find_mock):
        search_parameters = {'vendor_id': 1337,
                             'product_id': 42,
                             'device_release_number': 3}

        usb_devices = list(yak_server.usbdevice.find(**search_parameters))

        expected_keyword_args = {'idVendor': 1337,
                                 'idProduct': 42,
                                 'bcdDevice': 3}
        self.assertEqual(len(usb_devices), 1)
        self.assertEqual(usb_devices[0].raw_device, expected_keyword_args)

    @mock_usb_find()
    def test_find_usb_device_with_not_all_parameters(self, usb_find_mock):
        search_parameters = {'vendor_id': 1337,
                             'device_release_number': 3}

        usb_devices = list(yak_server.usbdevice.find(**search_parameters))

        expected_keyword_args = {'idVendor': 1337,
                                 'bcdDevice': 3}
        self.assertEqual(len(usb_devices), 1)
        self.assertEqual(usb_devices[0].raw_device, expected_keyword_args)

    @mock_usb_find(match_count=3)
    def test_find_usb_device_multiple_matches(self, mock_usb_find):
        search_parameters = {'vendor_id': 1337,
                             'device_release_number': 3}

        usb_devices = list(yak_server.usbdevice.find(**search_parameters))

        expected_keyword_args = {'idVendor': 1337,
                                 'bcdDevice': 3}
        self.assertEqual(len(usb_devices), 3)
        self.assertEqual(usb_devices[0].raw_device, expected_keyword_args)
        self.assertEqual(usb_devices[1].raw_device, expected_keyword_args)
        self.assertEqual(usb_devices[2].raw_device, expected_keyword_args)

    @mock_usb_find(match_count=0)
    def test_find_usb_device_multiple_matches(self, mock_usb_find):
        usb_devices = list(yak_server.usbdevice.find())

        self.assertEqual(usb_devices, [])
