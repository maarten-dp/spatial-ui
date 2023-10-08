from ..models.primitives import Vector4, Vector2
from ..models.style import BaseLayout
from ..helpers import AUTO


def handle_width_auto(width, margin_left, margin_right, underflow):
    return underflow, margin_left, margin_right


def handle_margin_auto(width, margin_left, margin_right, underflow):
    return width, underflow / 2, underflow / 2


def handle_margin_right_auto(width, margin_left, margin_right, underflow):
    return width, margin_left, underflow


def handle_margin_left_auto(width, margin_left, margin_right, underflow):
    return width, underflow, margin_left


def handle_no_auto(width, margin_left, margin_right, underflow):
    return width, margin_left, margin_right # + underflow


class BlockLayout(BaseLayout):
    float_left_offset: float = 0
    float_right_offset: float = 0
    float_top_offset: float = 0

    def render_layout(
        self,
        parent_layout,
        float_left_offset=0,
        float_right_offset=0,
        float_top_offset=0
    ):
        self.float_left_offset = float_left_offset
        self.float_right_offset = float_right_offset
        self.float_top_offset = float_top_offset

        self.calculate_width(parent_layout.container)
        self.calculate_position(parent_layout.container)
        self.layout_children()
        self.calculate_height(parent_layout.container)

    def calculate_width(self, parent_container):
        margin_width = 0

        with self.style(parent_container) as style:
            margin_left = style.margin_left
            margin_right = style.margin_right
            
            padding_left = style.padding_left
            padding_right = style.padding_right

            border_left = style.border_left_width
            border_right = style.border_right_width

            width = style.width

            width_is_auto = width == AUTO
            margin_right_is_auto = margin_right == AUTO
            margin_left_is_auto = margin_left == AUTO

            if width_is_auto:
                width = 0
            if margin_left_is_auto:
                margin_left = 0
            if margin_right_is_auto:
                margin_right = 0

            margin_width = margin_left + margin_right
            padding_width = padding_left + padding_right
            border_width = border_left + border_right

        total = margin_width + padding_width + border_width + width
        underflow = parent_container.content_box.width - total

        handlers = {
            (True, True, True): handle_width_auto,
            (True, False, True): handle_width_auto,
            (True, True, False): handle_width_auto,
            (True, False, False): handle_width_auto,
            (False, True, True): handle_margin_auto,
            (False, False, True): handle_margin_right_auto,
            (False, True, False): handle_margin_left_auto,
            (False, False, False): handle_no_auto,
        }

        key = (width_is_auto, margin_left_is_auto, margin_right_is_auto)
        width, margin_left, margin_right = handlers[key](
            width,
            margin_left,
            margin_right,
            underflow
        )

        padding = Vector4(
            x=padding_right,
            z=padding_left
        )
        border = Vector4(
            x=border_right,
            z=border_left
        )
        margin = Vector4(
            x=margin_right,
            z=margin_left
        )
        self.container.content.width = width
        self.container.padding += padding
        self.container.border += border
        self.container.margin += margin

    def calculate_position(self, parent_container):
        with self.style(parent_container) as style:
            margin_top = style.margin_top
            margin_bottom = style.margin_bottom
            if margin_top == AUTO:
                margin_top = 0
            if margin_bottom == AUTO:
                margin_bottom = 0

            padding_top = style.padding_top
            padding_bottom = style.padding_bottom

            border_top = style.border_top_width
            border_bottom = style.border_bottom_width

        padding = Vector4(
            w=padding_top,
            y=padding_bottom
        )
        border = Vector4(
            w=border_top,
            y=border_bottom
        )
        margin = Vector4(
            w=margin_top,
            y=margin_bottom
        )
        self.container.padding += padding
        self.container.border += border
        self.container.margin += margin

        topleft = parent_container.content_box.top_left
        x = topleft.x
        y = topleft.y
        non_content_offset = self.container.margin.z + self.container.border.z + self.container.padding.z
        x += non_content_offset
        y += margin_top + border_top + padding_top

        if self.style.float == "left":
            x += self.float_left_offset
            thresh = parent_container.width - self.float_right_offset
            if self.container.margin_box.width + x > thresh:
                y += parent_container.content_box.height
            else:
                y += self.float_top_offset
        if self.style.float == "right":
            x += parent_container.width - self.float_right_offset - self.container.margin_box.width
            if x < self.float_left_offset:
                y += parent_container.content_box.height
                x = (parent_container.content_box.right - self.container.margin_box.width) + non_content_offset
            else:
                y += self.float_top_offset
        else:
            y += parent_container.content_box.height

        self.container.content.top_left = Vector2(x=x, y=y)

    def layout_children(self):
        floating = []
        non_floating = []

        for child in self.children:
            if child.style.float in ['left', 'right']:
                floating.append(child)
            else:
                non_floating.append(child)

        left_float_offset = 0
        right_float_offset = 0
        top_float_offset = 0
        height = 0
        current_height = 0
        for child in floating:
            child.render_layout(
                self,
                left_float_offset,
                right_float_offset,
                top_float_offset,
            )
            if child.style.float == "left":
                left_float_offset += child.container.margin_box.width
            else:
                right_float_offset += child.container.margin_box.width

            height = max(child.container.margin_box.height, height)
            self.container.content.height = height + current_height

            if child.container.margin_box.top - self.container.content.top >= self.container.content.height:
                current_height += height
                self.container.content.height = height + current_height
                top_float_offset = height
                left_float_offset = 0
                right_float_offset = 0
                height = 0

        for child in non_floating:
            child.render_layout(self)
            self.container.content.height += child.container.margin_box.height

    def calculate_height(self, parent_container):
        with self.style(parent_container) as style:
            height = style.height
            min_height = style.min_height

        if height != AUTO:
            self.container.content.height = height

        if self.container.content.height < min_height:
            self.container.content.height = min_height
