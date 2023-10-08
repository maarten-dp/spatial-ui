from .primitives.element import Element


class Panel(Element):
    def __init__(self, *children):
        super().__init__()
        for child in children:
            self.add(child)
