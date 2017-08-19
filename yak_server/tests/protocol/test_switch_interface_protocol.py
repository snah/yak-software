#! /usr/bin/env python3

# pylint: disable = no-self-use, attribute-defined-outside-init

import time

import tests.util
import tests.doubles

from yak_server import usbdevice


TIMEOUT = 0.1


class SwitchInterfaceV0_0_1ProtocolTest:
    # pylint: disable = no-member
    DEVICE_CLASS_ID = usbdevice.DeviceClassID(vendor_id=0x04d8,
                                              product_id=0x5900,
                                              release_number=0x0001)

    def test_button_press_and_release(self):
        self.device = self._get_device()
        self.device.connect()
        self.device.flush()

        self.assertEqual(self.device.class_identifier, self.DEVICE_CLASS_ID)

        self._press_button(3)

        button_down_response = self.device.read(2)
        self.assertEqual(button_down_response, b'\x00\x04')
        self.device.flush()

        self._release_button(3)
        button_up_response = self.device.read(2)
        self.assertEqual(button_up_response, b'\x00\x00')

    def _press_button(self, button_number):
        raise NotImplementedError()

    def _release_button(self, button_number):
        raise NotImplementedError()

    def _get_device(self):
        raise NotImplementedError()


class TestRealSwitchInterfaceV0_0_1Protocol(SwitchInterfaceV0_0_1ProtocolTest,
                                            tests.util.RealDeviceTest):
    def _press_button(self, button_number):
        print('Press and hold the button for switch 3.')

    def _release_button(self, button_number):
        print('Release the button for switch 3.')

    def _get_device(self):
        devices = self._find_devices()
        if not devices:
            print('Please plugin the device.')
        while not devices:
            time.sleep(0.1)
            devices = self._find_devices()
        return devices[0]

    def _find_devices(self):
        return usbdevice.find_by_class_id(self.DEVICE_CLASS_ID)


class TestFakeSwitchInterfaceV0_0_1Protocol(SwitchInterfaceV0_0_1ProtocolTest,
                                            tests.util.FakeDeviceTest):
    def _press_button(self, button_number):
        self.fake_switch_device.press_button(button_number)

    def _release_button(self, button_number):
        self.fake_switch_device.release_button(button_number)

    def _get_device(self):
        self.fake_switch_device = tests.doubles.FakeSwitchDeviceV0_0_1()
        return self.fake_switch_device


class SwitchInterfaceV0_0_0ProtocolTest:
    # pylint: disable = no-member
    DEVICE_CLASS_ID = usbdevice.DeviceClassID(vendor_id=0x04d8,
                                              product_id=0x5900,
                                              release_number=0x0000)

    def test_button_press_and_release(self):
        self.device = self._get_device()
        self.device.connect()
        self.device.flush()

        self.assertEqual(self.device.class_identifier, self.DEVICE_CLASS_ID)

        self._press_button()

        button_down_response = self.device.read(1)
        self.assertEqual(button_down_response, b'\x01')
        self.device.flush()

        self._release_button()
        button_up_response = self.device.read(1)
        self.assertEqual(button_up_response, b'\x00')

    def _press_button(self):
        raise NotImplementedError()

    def _release_button(self):
        raise NotImplementedError()

    def _get_device(self):
        raise NotImplementedError()


class TestRealSwitchInterfaceV0_0_0Protocol(SwitchInterfaceV0_0_0ProtocolTest,
                                            tests.util.RealDeviceTest):
    def _press_button(self):
        print('Press and hold the button on the test jig.')

    def _release_button(self):
        print('Release the button on the test jig.')

    def _get_device(self):
        devices = self._find_devices()
        if not devices:
            print('Please plugin the device.')
        while not devices:
            time.sleep(0.1)
            devices = self._find_devices()
        return devices[0]

    def _find_devices(self):
        return usbdevice.find_by_class_id(self.DEVICE_CLASS_ID)


class TestFakeSwitchInterfaceV0_0_0Protocol(SwitchInterfaceV0_0_0ProtocolTest,
                                            tests.util.FakeDeviceTest):
    def _press_button(self):
        self.fake_switch_device.press_button()

    def _release_button(self):
        self.fake_switch_device.release_button()

    def _get_device(self):
        self.fake_switch_device = tests.doubles.FakeSwitchDeviceV0_0_0()
        return self.fake_switch_device
