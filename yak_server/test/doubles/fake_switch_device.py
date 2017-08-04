from yak_server import usbdevice


class FakeSwitchDevice:
    def __init__(self):
        self.read_buffer = b''

    def connect(self):
        pass

    def flush(self):
        pass

    def read(self, number_of_bytes):
        if self.read_buffer:
            response = self.read_buffer[:number_of_bytes]
            self.read_buffer = self.read_buffer[len(response):]
            return response
        else:
            raise usbdevice.USBError('No data available')

    def press_button(self):
        self.read_buffer += b'\x01'

    def release_button(self):
        self.read_buffer += b'\x00'
