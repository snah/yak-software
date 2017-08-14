#! /usr/bin/env python3

# pylint: disable = no-self-use, unused-argument

import unittest
import unittest.mock

from tests import util

import yak_server.events


class TestEvent(util.TestCase):
    def test_initialize_with_timestamp(self):
        event = yak_server.events.Event(timestamp='yesterday')

        self.assertEqual(event.timestamp, 'yesterday')

    def test_uses_current_time_if_none_given(self):
        datetime_patch_target = 'yak_server.events.datetime.datetime'
        with unittest.mock.patch(datetime_patch_target) as datetime_mock:
            event = yak_server.events.Event()

            self.assertEqual(event.timestamp, datetime_mock.now.return_value)
