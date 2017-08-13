#! /usr/bin/env python3

# pylint: disable = no-self-use

import threading
import unittest
import unittest.mock
import queue

from test import util

import yak_server.__main__
import yak_server.usbdevice
from yak_server import translators


MAX_WAIT_TIME = 2


class TestSingleSwitchSingleLamp(util.TestCase):
    """Test using a single switch to turn on and off a single lamp.

    Only a single switch and a single lamp are connected. Test that
    the switch can be used to turn the lamp on and off.
    """

    ITERATIONS = 3

    def setUp(self):
        self.start_patch('yak_server.usbdevice.find',
                         side_effect=self.map_mock_device)

        self.mock_switch_device = unittest.mock.Mock()
        self.mock_switch_device.read.side_effect = self.input_data_from_queue
        self.mock_switch_device.class_identifier = (
            0x04d8, 0x5900, 0x0000)

        self.mock_ac_device = unittest.mock.Mock()
        self.mock_ac_device.write.side_effect = self.queue_output_data
        self.mock_ac_device.class_identifier = (
            0x04d8, 0x5901, 0x0000)

        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()

        self.button_state = [False] * 8

        self.thread = threading.Thread(target=self.run_server)

    @util.run_for_iterations(ITERATIONS)
    def test_single_switch_single_lamp(self):
        self.start_server()

        self.press_button(0)
        self.assert_lamp_is_on()

        self.press_button(0)
        self.assert_lamp_is_off()

        self.press_button(0)
        self.assert_lamp_is_on()

        self.wait_for_server_shutdown()

    def map_mock_device(self, **kwargs):
        device_map = {(0x04d8, 0x5900): (self.mock_switch_device, ),
                      (0x04d8, 0x5901): (self.mock_ac_device, )}
        return device_map[(kwargs['vendor_id'], kwargs['product_id'])]

    def start_server(self):
        self.thread.start()

    def run_server(self):
        yak_server.__main__.main()

    def wait_for_server_shutdown(self):
        self.thread.join(2)

    def input_data_from_queue(self, number_of_bytes):
        # pylint: disable = unused-argument
        return self.input_queue.get()

    def queue_output_data(self, data):
        self.output_queue.put(data)

    def assert_all_data_was_read(self):
        self.assertTrue(self.input_queue.empty())

    def assert_lamp_is_on(self):
        self.assert_last_event(yak_server.events.LampOnEvent())

    def assert_lamp_is_off(self):
        self.assert_last_event(yak_server.events.LampOffEvent())

    def assert_last_event(self, event):
        data = self.output_queue.get(timeout=MAX_WAIT_TIME)
        ac_translator = translators.create_usb_translator(self.mock_ac_device)
        received_event = ac_translator.raw_data_to_event(data)
        self.assert_event_equal(received_event, event)
        self.assert_all_data_was_read()

    def press_button(self, button_number):
        # pylint: disable = unused-argument
        # Only one button is used currently, so button_number is ignored.
        if self.button_state[0]:
            self.input_queue.put(b'\x00')
            self.button_state[0] = False
        else:
            self.input_queue.put(b'\x01')
            self.button_state[0] = True
