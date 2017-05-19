import unittest
import unittest.mock


class TestCase(unittest.TestCase):
    def start_patch(self, target, *args, **kwargs):
        patch = unittest.mock.patch(target, *args, ** kwargs)
        patch.mock = patch.start()
        self.addCleanup(patch.stop)
        return patch


def return_first(first, *args, **kwars):
    return first
