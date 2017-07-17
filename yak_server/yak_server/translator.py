"""Defines translators for various interfaces."""


class SwitchInterfaceTranslator:
    """Translate USB messages from the switch interface to event."""

    def raw_data_to_event(self, raw_data):
        """Translate raw data to the corresponding event.

        The input is expected to be a bytes object.
        """
        self._check_raw_data_type(raw_data)
        if raw_data == b'\x00':
            return 'off'
        elif raw_data == b'\x01':
            return 'on'
        self._handle_unknown_message(raw_data)

    def event_to_raw_data(self, event):
        """Translate and event to raw data."""
        if event == 'off':
            return b'\x00'
        elif event == 'on':
            return b'\x01'
        self._handle_unknown_event(self)

    @staticmethod
    def maximum_data_length():
        """Return the maximum data length expected from the device."""
        return 1

    @staticmethod
    def _check_raw_data_type(raw_data):
        if not isinstance(raw_data, bytes):
            raise TypeError("'raw_data' should be a bytes object.")

    @staticmethod
    def _handle_unknown_message(raw_data):
        raise ValueError('Unknown message code {}'.format(raw_data))

    @staticmethod
    def _handle_unknown_event(event):
        raise ValueError("Unknown event type: '{}'".format(event))
