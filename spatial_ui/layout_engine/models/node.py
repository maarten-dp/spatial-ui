from enum import Enum, auto
from typing import List, Optional, Any

from pydantic import Field

from .base import BaseModel


class NodeType(Enum):
    ELEMENT = auto()
    CARET = auto()
    PLACEHOLDER = auto()
    TEXT = auto()
    SCROLLBAR = auto()


class Node(BaseModel):
    node_type: NodeType = NodeType.ELEMENT
    node_element_name: str
    node_class: Optional[str]
    node_id: Optional[str]
    raw_content: Optional[Any]
    children: List["Node"] = Field(default_factory=list)

    def __hash__(self):
        return id(self)

    def add(self, node: "Node") -> None:
        self.children.append(node)

    def add_all(self, *nodes: "Node") -> None:
        self.children.extend(nodes)

    @property
    def identifiers(self):
        base_identity =  {
            'class': self.node_class
        }
        if self.node_id:
            base_identity['id'] = self.node_id

