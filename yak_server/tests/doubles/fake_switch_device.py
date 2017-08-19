import queue

from yak_server import usbdevice


class FakeUsbDeviceBase:
    DEVICE_CLASS_ID = None

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
        if len(self._read_buffer) < number_of_bytes:
            self._update_read_buffer()
        return self._get_read_data(number_of_bytes)

    @property
    def class_identifier(self):
        return self.DEVICE_CLASS_ID

    def _update_read_buffer(self):
        self._read_buffer += self._read_queue.get()

    def _get_read_data(self, number_of_bytes):
        response = self._read_buffer[:number_of_bytes]
        self._read_buffer = self._read_buffer[len(response):]
        return response


class FakeSwitchDeviceV0_0_1(FakeUsbDeviceBase):
    DEVICE_CLASS_ID = usbdevice.DeviceClassID(vendor_id=0x04d8,
                                              product_id=0x5900,
                                              release_number=0x0001)

    def __init__(self):
        super().__init__()
        self.button_state = [False] * 8

    def press_button(self, button_number):
        self.button_state[button_number - 1] = True
        self._send_button_state()

    def release_button(self, button_number):
        self.button_state[button_number - 1] = False
        self._send_button_state()

    def _send_button_state(self):
        self._read_queue.put(b'\x00' + self._button_data())

    def _button_data(self):
        buttons_down = (i for i, state in enumerate(self.button_state)
                        if state)
        data = sum(2 ** i for i in buttons_down)
        return bytes([data])


class FakeSwitchDeviceV0_0_0(FakeUsbDeviceBase):
    DEVICE_CLASS_ID = usbdevice.DeviceClassID(vendor_id=0x04d8,
                                              product_id=0x5900,
                                              release_number=0x0000)

    def press_button(self):
        self._read_queue.put(b'\x01')

    def release_button(self):
        self._read_queue.put(b'\x00')


class FakeSwitchDevice(FakeSwitchDeviceV0_0_1):
    pass
