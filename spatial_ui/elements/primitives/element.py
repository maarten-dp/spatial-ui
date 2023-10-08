from ...events.signals import (
    ON_HOVER,
    ON_ENTER,
    ON_EXIT,
    ON_DOWN,
    ON_DOWN,
    ON_UP,
    ON_CLICK,
    ON_FOCUS,
    ON_BLUR,
    ON_FRAME
)

EVENTS = {
    "on_hover": ON_HOVER,
    "on_enter": ON_ENTER,
    "on_exit": ON_EXIT,
    "on_down": ON_DOWN,
    "on_down": ON_DOWN,
    "on_up": ON_UP,
    "on_click": ON_CLICK,
    "on_focus": ON_FOCUS,
    "on_blur": ON_BLUR,
    "on_frame": ON_FRAME
}


class Element:
    def __init__(self):
        self.parent = None
        self.children = [Scrollbar()]

    def __iter__(self):
        return iter(self.children)

    def add(self, child):
        if isinstance(child, Element):
            if child.parent:
                raise ValueError(f"{child} already has a parent {child.parent}")
            child.parent = self
        elif not isinstance(child, str):
            raise ValueError(f"Child must be Element or str, not {type(child)}")
        self.children.append(child)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {len(self.children)} children>"

    def register_system_events(self, layout):
        for event, signal in EVENTS.items():
            if hasattr(self, event):
                handler = getattr(self, event)
                signal.connect(handler, layout)


class Scrollbar(Element):
    def __init__(self):
        self.parent = None
        self.children = []

