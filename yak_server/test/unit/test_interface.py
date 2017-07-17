#! /usr/bin/env python3

# pylint: disable = no-self-use, unused-argument

import unittest
import unittest.mock

from test import util

import yak_server.interface


class TestUSBInterface(util.TestCase):
    def test_initialize_connects_to_usb_device(self):
        mock_usbdevice = unittest.mock.Mock()
        interface = yak_server.interface.USBInterface(mock_usbdevice)

        interface.initialize()

        mock_usbdevice.connect.assert_called_once()

    def test_receives_event(self):
        stub_usbdevice = unittest.mock.Mock()
        stub_usbdevice.read.side_effect = lambda n: b'abc'[:n]
        stub_translator = unittest.mock.Mock()
        stub_translator.raw_data_to_event.side_effect = lambda x: x + b'_event'
        stub_translator.maximum_data_length.return_value = 1
        interface = yak_server.interface.USBInterface(stub_usbdevice)
        interface.translator = stub_translator

        event = interface.get_event()

        self.assertEqual(event, b'a_event')

    def test_send_command(self):
        mock_usbdevice = unittest.mock.Mock()
        stub_translator = unittest.mock.Mock()
        stub_translator.event_to_raw_data.side_effect = lambda x: x[:1]
        interface = yak_server.interface.USBInterface(mock_usbdevice)
        interface.translator = stub_translator

        interface.send_command(b'a_event')

        mock_usbdevice.write.assert_called_once_with(b'a')


class TestInterfaceManager(util.TestCase):
    def test_find_input_interfaces(self):
        # pylint: disable = protected-access
        interface_manager = yak_server.interface.InterfaceManager()
        connected_devices = ['device1', 'device2']

        usb_find_patch = unittest.mock.patch('yak_server.usbdevice.find',
                                             return_value=connected_devices)
        with usb_find_patch as mock_usb_find:
            interfaces = interface_manager.input_interfaces()

            mock_usb_find.assert_called_once_with(vendor_id=0x04d8,
                                                  product_id=0x5900)

        devices = [interface._usb_device for interface in interfaces]
        self.assertCountEqual(devices, connected_devices)

    def test_find_output_interfaces(self):
        # pylint: disable = protected-access
        interface_manager = yak_server.interface.InterfaceManager()
        connected_devices = ['device1', 'device2']

        usb_find_patch = unittest.mock.patch('yak_server.usbdevice.find',
                                             return_value=connected_devices)
        with usb_find_patch as mock_usb_find:
            interfaces = interface_manager.output_interfaces()

            mock_usb_find.assert_called_once_with(vendor_id=0x04d8,
                                                  product_id=0x5901)

        devices = [interface._usb_device for interface in interfaces]
        self.assertCountEqual(devices, connected_devices)