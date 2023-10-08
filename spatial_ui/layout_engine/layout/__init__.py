from pydantic import BaseModel, Field

from .block import BlockLayout
from .text import TextLayout
from .misc import CaretLayout, ScrollbarLayout
from .table import TableRowLayout, TableCellLayout
from ..models.style import BaseLayout, BoxModel, Style


class AnonymousLayout(BaseModel):
    container: BoxModel = Field(default_factory=BoxModel)
