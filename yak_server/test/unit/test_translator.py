#! /usr/bin/env python3

# pylint: disable = no-self-use, unused-argument

import unittest
import unittest.mock

from test import util

import yak_server.translator


class TestSwitchInterfaceTranslator(util.TestCase):
    def setUp(self):
        self.translator = yak_server.translator.SwitchInterfaceTranslator()

    def test_translates_lamp_on_message_to_event(self):
        event = self.translator.raw_data_to_event(b'\x01')

        self.assertEqual(event, 'on')

    def test_translates_lamp_off_message_to_event(self):
        event = self.translator.raw_data_to_event(b'\x00')

        self.assertEqual(event, 'off')

    def test_raw_to_event_raises_value_error_on_unknown_input(self):
        with self.assertRaises(ValueError):
            self.translator.raw_data_to_event(b'\x11')

    def test_raw_to_event_raises_type_error_on_wrong_input_type(self):
        with self.assertRaises(TypeError):
            self.translator.raw_data_to_event(True)

    def test_translates_lamp_on_event_to_raw_data(self):
        raw_data = self.translator.event_to_raw_data('on')

        self.assertEqual(raw_data, b'\x01')

    def test_translates_lamp_off_event_to_raw_data(self):
        raw_data = self.translator.event_to_raw_data('off')

        self.assertEqual(raw_data, b'\x00')

    def test_event_to_raw_data_raises_value_error_on_unknown_event_type(self):
        with self.assertRaises(ValueError):
            self.translator.event_to_raw_data('unknown')

    @unittest.skip
    def test_event_to_raw_data_raises_type_error_if_not_given_and_event(self):
        self.fail('TODO')

    def test_correct_maximum_data_length(self):
        maximum_data_length = self.translator.maximum_data_length()

        self.assertEqual(maximum_data_length, 1)
