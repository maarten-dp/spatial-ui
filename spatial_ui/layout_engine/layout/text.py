import string
from typing import Any, List

from pydantic import BaseModel, Field

from ..models.primitives import Vector4, Vector2, Rect
from ..models.style import BaseLayout
from ..helpers import AUTO
from ..fonts import get_font


def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    _, descent = font.getmetrics()

    _, _, width, height = font.getmask(text_string).getbbox()
    text_width = width
    text_height = height + descent

    return (text_width, text_height)


def avg_font_size(font):
    width, _ = get_text_dimensions(string.ascii_letters, font)
    return width / len(string.ascii_letters)


class TextLine(BaseModel):
    text: str
    font: Any
    box: Any



class TextLayout(BaseLayout):
    text_blocks: List[TextLine] = Field(default_factory=list)

    def render_layout(
        self,
        parent_layout,
        *args, **kwargs
    ):
        rendered_lines = []

        size = int(self.style.font_size.value)
        font = get_font(self.style.font_family, size)
        line_height = self.style.line_height.value

        text = self.node.raw_content

        avg_size = avg_font_size(font)

        estimated_chars_per_line = int(parent_layout.container.width // avg_size)
        estimated_chars_per_line = 100
        previous_idx = 0

        max_width = parent_layout.container.width
        y = parent_layout.container.content_box.top
        x = parent_layout.container.content_box.left

        line = text[previous_idx:estimated_chars_per_line]
        while line:
            width, height, line = self._get_size(line, max_width, font)

            line_rect = Rect(
                x=x,
                y=y,
                width=width,
                height=height
            )

            text_line = TextLine(
                text=line,
                font=font,
                box=line_rect,
            )
            self.text_blocks.append(text_line)
            previous_idx += len(line) + 1
            y += height + line_height
            line = text[previous_idx:previous_idx + estimated_chars_per_line]

        self.container.content.height = y - parent_layout.container.content_box.top
        if len(self.text_blocks) == 1:
            self.container.content.width = self.text_blocks[0][0].width
        else:
            self.container.content.width = parent_layout.container.content.width
        self.container.content.top_left = parent_layout.container.content.top_left

    def _get_size(self, line, max_width, font):
        line_size, height = get_text_dimensions(line, font)
        while line_size > max_width:
            line = line.rsplit(' ', 1)[0]
            line_size, height = get_text_dimensions(line, font)
        return line_size, height, line




