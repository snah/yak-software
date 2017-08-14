import unittest
import unittest.mock

import yak_server.usbdevice


class TestCase(unittest.TestCase):
    def start_patch(self, target, *args, **kwargs):
        patch = unittest.mock.patch(target, *args, ** kwargs)
        patch.mock = patch.start()
        self.addCleanup(patch.stop)
        return patch

    def assert_event_equal(self, first, second):
        """Assert that two events are equal for all except timestamp."""
        EventClass = type(second)
        event_timestamp = first.timestamp
        time_corrected_event = EventClass(second, timestamp=event_timestamp)
        self.assertEqual(first, time_corrected_event)


class RealDeviceTest(TestCase):
    """Base class for testing the protocol of actual devices."""

    DEVICE_CLASS_ID = None

    def setUp(self):
        if not self._device_connected():
            self.skipTest('Device not connected.')

    def _device_connected(self):
        search_parameters = {'vendor_id': self.DEVICE_CLASS_ID.vendor_id,
                             'product_id': self.DEVICE_CLASS_ID.product_id,
                             'release_number': self.DEVICE_CLASS_ID.release_number}
        return bool(yak_server.usbdevice.find(**search_parameters))


class FakeDeviceTest(TestCase):
    """Base class for testing the protocol of fakes."""


def return_first(first, *args, **kwars):
    """Return the first of a functions arguments."""
    # pylint: disable = unused-argument
    return first


def run_for_iterations(count):
    """Run the server for 'count' iterations."""
    patch_target = 'yak_server.__main__.Application.server_running'
    return unittest.mock.patch(patch_target,
                               new=_return_true_for_iterations(count))


def _return_true_for_iterations(count):
    def generator():
        for i in range(count):
            yield True
        yield False
    return generator().__next__
