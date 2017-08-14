#! /usr/bin/env python3

# pylint: disable = no-self-use, unused-argument

from tests import util

import yak_server.translators
import yak_server.events


class TestLookupTranslator(util.TestCase):
    class ConcreteLookupTranslator(yak_server.translators.LookupTranslator):
        DEVICE_CLASS_ID = None
        TRANSLATION_TABLE = yak_server.translators.LookupTable({
            b'a': yak_server.events.ButtonUpEvent,
            b'b': yak_server.events.ButtonDownEvent})

    def setUp(self):
        self.translator = self.ConcreteLookupTranslator()

    def test_translates_raw_data_to_event(self):
        event = self.translator.raw_data_to_event(b'b')

        self.assert_event_equal(event, yak_server.events.ButtonDownEvent())

    def test_raw_to_event_raises_value_error_on_unknown_input(self):
        with self.assertRaises(ValueError):
            self.translator.raw_data_to_event(b'\x11')

    def test_raw_to_event_raises_type_error_on_wrong_input_type(self):
        with self.assertRaises(TypeError):
            self.translator.raw_data_to_event(True)

    def test_translates_event_to_raw_data(self):
        event = yak_server.events.ButtonUpEvent()
        raw_data = self.translator.event_to_raw_data(event)

        self.assertEqual(raw_data, b'a')

    def test_event_to_raw_data_raises_value_error_on_unknown_event_type(self):
        with self.assertRaises(ValueError):
            self.translator.event_to_raw_data(yak_server.events.Event())

    def test_event_to_raw_data_raises_type_error_if_not_given_an_event(self):
        with self.assertRaises(TypeError):
            self.translator.event_to_raw_data('not an event')

    def test_correct_maximum_data_length(self):
        maximum_data_length = self.translator.maximum_data_length()

        self.assertEqual(maximum_data_length, 1)
