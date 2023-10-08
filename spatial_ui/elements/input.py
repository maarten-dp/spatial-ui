from .primitives.element import Element
from ..events.signals import (
    ON_CHAR,
    ON_ENTER_KEY,
    ON_BACKSPACE_KEY,
    ON_ARROW_KEY
)

class Caret(Element):
    def __init__(self):
        super().__init__()
        self.layout = None

    def set_layout(self, layout):
        # TODO: figure out a way to decouple the layout from the element
        # Or at least, more coherent
        self.layout = layout
        self.counter = 0


class Placeholder(Element):
    def __init__(self, text):
        super().__init__()
        self.add(text)


class Text(Element):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def __bool__(self):
        return bool(self.text)

    def __getitem__(self, key):
        return self.text[key]
        if isinstance(key, slice):
            import pdb; pdb.set_trace()
            indices = range(*key.indices(len(self.list)))
            return [self.list[i] for i in indices]
        return self.list[key]


class Input(Element):
    def __init__(self, placeholder=None):
        super().__init__()
        self.caret = Caret()
        if placeholder:
            placeholder = Placeholder(placeholder)
            self.add(placeholder)
        self.placeholder = placeholder
        self._content_container = Text("")
        self.add(self.caret)
        self.add(self._content_container)

        self._content = []
        self._index = 0

    @property
    def must_draw(self):
        return not bool(self._content)

    def on_focus(self, layout):
        self._connect_keyboard()

    def on_blur(self, layout):
        self._disconnect_keyboard()

    def _connect_keyboard(self):
        ON_CHAR.connect(self.on_char)
        # ON_ENTER_KEY.connect(self.on_enter_key)
        ON_BACKSPACE_KEY.connect(self.on_backspace_key)
        ON_ARROW_KEY.connect(self.on_arrow_key)

    def _disconnect_keyboard(self):
        ON_CHAR.disconnect(self.on_char)
        # ON_ENTER_KEY.disconnect(self.on_enter_key)
        ON_BACKSPACE_KEY.disconnect(self.on_backspace_key)
        ON_ARROW_KEY.disconnect(self.on_arrow_key)

    def on_char(self, char):
        self._content.append(char)
        self._index += 1
        self._content_container.text = "".join(self._content)

    def on_enter_key(self):
        pass

    def on_backspace_key(self, sender):
        if not self._index:
            return
        self._index -= 1
        self._content.pop(self._index)
        self._content_container.text = "".join(self._content)

    def on_arrow_key(self, arrow):
        if arrow == "right" and self._index < len(self._content):
            self._index += 1
        if arrow == "left" and self._index:
            self._index -= 1
