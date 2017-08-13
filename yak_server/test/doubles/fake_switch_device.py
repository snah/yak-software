import queue

from yak_server import usbdevice


class FakeSwitchDevice:
    def __init__(self):
        self._read_buffer = b''
        self._read_queue = queue.Queue()

    def connect(self):
        pass

    def flush(self):
        self._read_buffer = b''
        while not self._read_queue.empty():
            self._read_queue.get()

    def read(self, number_of_bytes):
        self._update_read_buffer()
        if self._read_buffer:
            response = self._read_buffer[:number_of_bytes]
            self._read_buffer = self._read_buffer[len(response):]
            return response
        else:
            raise usbdevice.USBError('No data available')

    def press_button(self):
        self._read_queue.put(b'\x01')

    def release_button(self):
        self._read_queue.put(b'\x00')

    def _update_read_buffer(self):
        while not self._read_queue.empty():
            self._read_buffer += self._read_queue.get()
