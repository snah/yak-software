import unittest
import unittest.mock
from unittest.mock import call

from test import util

from yak_server import __main__

class TestMain(util.TestCase):
    """Temporary test for main function.
    
    Replace as soon as possible with proper functional test that
    mocks the internal representation of USB devices and with unit
    test for these classes.
    """

    ITERATIONS = 5

    def setUp(self):
        self.mock_usb = self.start_patch('yak_server.__main__.usb', new=unittest.mock.MagicMock()).mock
        self.start_patch('yak_server.__main__.server_running', new=self.run_for_iterations(self.ITERATIONS))

    def run_for_iterations(self, count):
        def generator():
            for i in range(count):
                yield True
            yield False
        return generator().__next__

    def test_main_calls_correct_functons(self):
        __main__.main()

        switch_device_call = call.core.find(idProduct=0x04d8, idVendor=0x5901)
        AC_device_call = call.core.find(idProduct=0x04d8, idVendor=0x5901)

        switch_device = self.mock_usb.core.find(idProduct=0x04d8, idVendor=0x5901)
        AC_device = self.mock_usb.core.find(idProduct=0x04d8, idVendor=0x5901)

        switch_conf = switch_device.get_active_configuration()
        switch_interface = switch_conf.interfaces()[0]
        switch_endpoint = switch_interface.endpoints()[0]

        AC_conf = AC_device.get_active_configuration()
        AC_interface = AC_conf.interfaces()[0]
        AC_endpoint = AC_interface.endpoints()[0]

        manager_mock = unittest.mock.MagicMock()
        manager_mock.switch_endpoint = switch_endpoint
        manager_mock.AC_endpoint = AC_endpoint

        self.mock_usb.assert_has_calls([call.core.find(idProduct=0x05d8, idVendor=0x5900).detach_kernel_driver(0)])
        self.mock_usb.assert_has_calls([call.util.claim_interface(switch_device, 0)])

        self.mock_usb.assert_has_calls([call.core.find(idProduct=0x05d8, idVendor=0x5901).detach_kernel_driver(0)])
        self.mock_usb.assert_has_calls([call.util.claim_interface(switch_device, 0)])

        read_calls = [True for call in switch_endpoint.mock_calls if call == call.read(1)]
        number_of_read_calls = sum(read_calls)
        self.assertEqual(number_of_read_calls, self.ITERATIONS)

        read_data = switch_endpoint.read(1)

        write_calls = [True for call in AC_endpoint.mock_calls if call == call.write(read_data)]
        number_of_write_calls = sum(write_calls)
        self.assertEqual(number_of_write_calls, self.ITERATIONS)
