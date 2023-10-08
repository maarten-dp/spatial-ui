from ..models.style import BaseLayout
from ..models.primitives import Vector2


class CaretLayout(BaseLayout):
    def render_layout(self, parent_layout):
        container = parent_layout.container
        self.container.content = container.content.copy()
        self.container.content.width = self.style.width.value;
        line_height = self.style.line_height.value or self.style.font_size.value
        if self.style.height == 'auto':
            height = line_height
        else:
            height = self.style.height.value
        offset = line_height - height
        # figure out why the height is off center
        offset += 2

        self.container.content.height = height
        self.container.content.y += offset


class ScrollbarLayout(BaseLayout):
    def render_layout(self, parent_layout):
        container = parent_layout.container

        self.container.content.width = self.style.width.value;
        self.container.content.height = 100

        top_right = container.content.top_left
        top_right.x += container.content.width - self.container.content.width
        self.container.content.topleft = top_right
