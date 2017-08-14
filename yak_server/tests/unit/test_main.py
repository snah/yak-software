#! /usr/bin/env python3

# pylint: disable = no-self-use, unused-argument

import unittest
import unittest.mock

from tests import util

import yak_server.__main__


MAIN_LOOP_PATCH_TARGET = 'yak_server.__main__.Application.main_loop_iteration'


class TestApplication(util.TestCase):
    @util.run_for_iterations(0)
    def test_main_loop_does_nothing_if_server_not_running(self):
        main_loop_iterator_mock = self.start_patch(MAIN_LOOP_PATCH_TARGET).mock
        application = yak_server.__main__.Application()

        application.main_loop()

        main_loop_iterator_mock.assert_not_called()

    @util.run_for_iterations(3)
    def test_main_loop_iterates_untill_server_stopped(self):
        main_loop_iterator_mock = self.start_patch(MAIN_LOOP_PATCH_TARGET).mock
        application = yak_server.__main__.Application()

        application.main_loop()

        self.assertEqual(main_loop_iterator_mock.call_count, 3)

    def test_main_loop_iteration_gets_event(self):
        application_mock = unittest.mock.Mock()

        yak_server.__main__.Application.main_loop_iteration(application_mock)

        application_mock.get_event.assert_called_once()

    def test_main_loop_iteration_handles_event(self):
        application_mock = unittest.mock.Mock()

        yak_server.__main__.Application.main_loop_iteration(application_mock)

        expected_arg = application_mock.get_event.return_value
        application_mock.handle_event.assert_called_once_with(expected_arg)


class TestMainFunction(util.TestCase):
    def setUp(self):
        application_patch = self.start_patch('yak_server.__main__.Application')
        self.application_mock = application_patch.mock.return_value

    def test_main_function_calls_main_loop(self):
        yak_server.__main__.main()

        self.application_mock.main_loop.assert_called_once()

    def test_main_function_calls_setup_before_main_loop(self):
        expected_calls = (unittest.mock.call.setup(),
                          unittest.mock.call.main_loop())

        yak_server.__main__.main()

        self.application_mock.assert_has_calls(expected_calls)
