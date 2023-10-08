# from .primitives.clickable import Clickable
from .primitives.element import Element

class Button(Element):
    def __init__(self, text=None):
        super().__init__()
        if text:
            self.add(text)

