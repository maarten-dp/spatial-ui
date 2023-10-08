from ..models.primitives import Vector4, Vector2
from ..models.style import BaseLayout
from .block import BlockLayout


class TableCellLayout(BaseLayout):
    column_idx: int

    def render_layout(self, parent_layout):
        index = self.column_idx
        
        children_amount = len(parent_layout.children)

        with self.style(parent_layout.container) as style:
            padding_left = style.padding_left
            padding_right = style.padding_right
            padding_top = style.padding_top
            padding_bottom = style.padding_bottom

            padding_width = padding_left + padding_right

            border_top = style.border_top_width
            border_bottom = style.border_bottom_width
            border_left = style.border_left_width
            border_right = style.border_right_width
            border_width = border_left + border_right

        padding = Vector4(
            x=padding_right,
            z=padding_left,
            w=padding_top,
            y=padding_bottom
        )
        border = Vector4(
            x=border_right,
            z=border_left,
            w=border_top,
            y=border_bottom
        )

        width = parent_layout.container.content.width
        base_x = parent_layout.container.content.x + (padding_left + border_left)
        cell_width = (width / children_amount)

        self.container.content.x = base_x + (cell_width * index)
        self.container.content.y = parent_layout.container.content_box.y + (padding_top + border_top)
        self.container.content.width = cell_width - (padding_width + border_width)
        self.container.padding += padding
        self.container.border += border
        self.container.content.height = self.container.margin_box.height

        for child in self.children:
            child.render_layout(self)
            self.container.content.height += child.container.margin_box.height


class TableRowLayout(BlockLayout):
    def render_layout(self, parent_layout):
        self.container = parent_layout.container.copy()

        with self.style(parent_layout.container) as style:
            padding_left = style.padding_left
            padding_right = style.padding_right
            padding_top = style.padding_top
            padding_bottom = style.padding_bottom

            padding_width = padding_left + padding_right

            border_top = style.border_top_width
            border_bottom = style.border_bottom_width
            border_left = style.border_left_width
            border_right = style.border_right_width

            border_width = border_left + border_right

        padding = Vector4(
            x=padding_right,
            z=padding_left,
            w=padding_top,
            y=padding_bottom
        )
        border = Vector4(
            x=border_right,
            z=border_left,
            w=border_top,
            y=border_bottom
        )
        self.container.padding += padding
        self.container.border += border
        self.container.content.x += padding_left + border_left
        self.container.content.width -= padding_width + border_width

        parent_y = parent_layout.container.content_box.y
        current_height = self.container.margin_box.height - (padding_bottom + border_bottom)
        self.container.content.y = parent_y + current_height

        max_height = 0
        for child in self.children:
            child.render_layout(self)
            max_height = max(child.container.content.height, max_height)
        for child in self.children:
            child.container.content.height = max_height
        self.container.content.height = child.container.margin_box.height
