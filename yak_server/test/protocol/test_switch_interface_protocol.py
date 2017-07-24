#! /usr/bin/env python3

# pylint: disable = no-self-use

import time
import usb

from test import util

import yak_server.usbdevice


class TestSwitchInterfaceProtocol(util.TestCase):
    def test_button_press_and_release(self):
        device = self._get_device()
        device.connect()

        while device.read(1):
            pass

        print('Press and hold the button on the test jig.')

        #FIXME in actual code:
        button_down_response = b''
        while not button_down_response:
            button_down_response = device.read(1)

        #FIXME in actual code:
        button_down_response = bytes(button_down_response)

        self.assertEqual(button_down_response, b'\x01')

        self.assertEqual(len(device.read(1)), 0)

        print('Release the button on the test jig.')

        #FIXME in actual code:
        button_up_response = b''
        while not button_up_response:
            button_up_response = device.read(1)

        #FIXME in actual code:
        button_up_response = bytes(button_up_response)

        self.assertEqual(button_up_response, b'\x00')


    def _get_device(self):
        devices = self._find_devices()
        if not devices:
            print('Please plugin the device.')
        while not devices:
            time.sleep(0.1)
            devices = self._find_devices()
        return devices[0]

    @staticmethod
    def _find_devices():
        return yak_server.usbdevice.find(vendor_id=0x04d8, product_id=0x5900)
