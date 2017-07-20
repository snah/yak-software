"""Defines translators for various interfaces."""

from yak_server import events


class LookupTable(dict):
    """One to one mapping with forward and reverse lookup."""

    def lookup(self, key):
        """Perform forward lookup."""
        return self[key]

    def reverse_lookup(self, value):
        """Preform reverse lookup."""
        try:
            return next(k for k, v in self.items() if value == v)
        except StopIteration:
            raise KeyError(value)


class SwitchInterfaceTranslator:
    """Translate USB messages from the switch interface to event."""

    translation_table = LookupTable({
        b'\x00': events.ButtonUpEvent,
        b'\x01': events.ButtonDownEvent})

    def raw_data_to_event(self, raw_data):
        """Translate raw data to the corresponding event.

        The input is expected to be a bytes object.
        """
        self._check_raw_data_type(raw_data)
        try:
            EventType = self._lookup_event_type(raw_data)
            return EventType()
        except KeyError:
            self._handle_unknown_message(raw_data)

    def event_to_raw_data(self, event):
        """Translate and event to raw data."""
        try:
            return self._lookup_raw_data(event)
        except KeyError:
            self._handle_unknown_event(self)

    @staticmethod
    def maximum_data_length():
        """Return the maximum data length expected from the device."""
        return 1

    def _lookup_event_type(self, raw_data):
        return self.translation_table.lookup(raw_data)

    def _lookup_raw_data(self, event):
        return self.translation_table.reverse_lookup(type(event))

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
