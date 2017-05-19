import unittest
import unittest.mock

from test import util

from yak_server import __main__

class TestMain(util.TestCase):
    """Temporary test for main function.
    
    Replace as soon as possible with proper functional test that
    mocks the internal representation of USB devices and with unit
    test for these classes.
    """
    def setUp(self):
        self.mock_usb = self.start_patch('yak_server.__main__.usb').mock
        self.start_patch('yak_server.__main__.server_running', new=self.run_for_iterations(5))

    def run_for_iterations(self, count):
        def generator():
            for i in range(count):
                yield True
            yield False
        return generator().__next__

    def test_main(self):
        __main__.main()

        print(self.mock_usb.mock_calls)

        self.mock_usb.assert_has_calls([
            unittest.mock.call.core.find(idProduct=22784, idVendor=1240),
            unittest.mock.call.core.find(idProduct=22785, idVendor=1240).detach_kernel_driver(0),
            ], any_order=False)
