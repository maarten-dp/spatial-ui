from functools import partialmethod
from blinker import Signal
from ...events.signals import (
    ON_CLICK,
    ON_DOWN,
    ON_UP,
    ON_HOVER,
    ON_ENTER,
    ON_EXIT,
    ON_FOCUS,
    ON_BLUR,
)

EVENTS = {
    "on_click": ON_CLICK,
    "on_down": ON_DOWN,
    "on_up": ON_UP,
    "on_hover": ON_HOVER,
    "on_enter": ON_ENTER,
    "on_exit": ON_EXIT,
    "on_focus": ON_FOCUS,
    "on_blur": ON_BLUR,
}


class PopulatedEvents(type(object)):
    def __init__(cls, name, bases, clsdict):
        for name, event in EVENTS.items():
            setattr(cls, name, partialmethod(cls.add_event, event))
            setattr(cls, f"remove_{name}", partialmethod(cls.remove_event, event))
            setattr(cls, f"trigger_{name}", partialmethod(cls.trigger_event, event))

        super().__init__(name, bases, clsdict)


class MouseInteractable(metaclass=PopulatedEvents):
    def add_event(self, event, handler):
       event.connect(handler, sender=self)

    def remove_event(self, event, handler):
       event.disconnect(handler, sender=self)

    def trigger_event(self, event):
       event.send(self)
