#! /usr/bin/env python3

import unittest
import unittest.mock

from test import util

import yak_server.__main__

class TestApplication(util.TestCase):
    @util.run_for_iterations(0)
    def test_main_loop_does_nothing_if_server_not_running(self):
        self.main_loop_iteration_mock = self.start_patch('yak_server.__main__.Application.main_loop_iteration').mock
        application = yak_server.__main__.Application()

        application.main_loop()

        self.main_loop_iteration_mock.assert_not_called()

    @util.run_for_iterations(3)
    def test_main_loop_iterates_untill_server_stopped(self):
        self.main_loop_iteration_mock = self.start_patch('yak_server.__main__.Application.main_loop_iteration').mock
        application = yak_server.__main__.Application()

        application.main_loop()

        self.assertEqual(self.main_loop_iteration_mock.call_count, 3)

    def test_main_loop_iteration_gets_event(self):
        application_mock = unittest.mock.Mock()

        yak_server.__main__.Application.main_loop_iteration(application_mock)

        application_mock.get_event.assert_called_once()

    def test_main_loop_iteration_handles_event(self):
        application_mock = unittest.mock.Mock()

        yak_server.__main__.Application.main_loop_iteration(application_mock)

        application_mock.handle_event.assert_called_once_with(application_mock.get_event.return_value)


class TestMainFunction(util.TestCase):
    def setUp(self):
        self.application_mock = self.start_patch('yak_server.__main__.Application').mock.return_value

    def test_main_function_calls_main_loop(self):
        yak_server.__main__.main()

        self.application_mock.main_loop.assert_called_once()

    def test_main_function_calls_setup_before_main_loop(self):
        expected_calls = (unittest.mock.call.setup(), unittest.mock.call.main_loop())

        yak_server.__main__.main()
        
        self.application_mock.assert_has_calls(expected_calls)
