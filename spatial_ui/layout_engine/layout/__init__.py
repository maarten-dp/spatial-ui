from pydantic import BaseModel, Field

from .block import BlockLayout
from .text import TextLayout
from ..models.style import BaseLayout, BoxModel


class AnonymousLayout(BaseModel):
    container: BoxModel = Field(default_factory=BoxModel)

    def render_layout(self, *args, **kwargs):
        for child in self.childeren:
            child.render_layout(self)
