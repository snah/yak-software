import datetime

import ezvalue

class Event(ezvalue.Value):
    """Baseclass for all events."""

    timestamp = 'The time the event was created.'

    def __init__(self, *args, **kwargs):
        """Initialize the event.

        All fields are required except for timestamp, which will be
        filled with the current time if omitted.
        """
        try:
            super().__init__(*args, **kwargs)
        except AttributeError:
            timestamp = datetime.datetime.now()
            super().__init__(*args, timestamp=timestamp, **kwargs)


class ButtonDownEvent(Event):
    """Emitted when a button or lightswitch was pressed down."""


class ButtonUpEvent(Event):
    """Emitted when a button or lightswitch was released."""
