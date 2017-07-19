import unittest
import unittest.mock


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
