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


def run_for_iterations(count):
    return unittest.mock.patch('yak_server.__main__.Application.server_running',
                               new=return_true_for_iterations(count))

def return_true_for_iterations(count):
    def generator():
        for i in range(count):
            yield True
        yield False
    return generator().__next__
