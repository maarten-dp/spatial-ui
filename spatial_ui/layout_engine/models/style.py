from typing import List, Dict
from collections import defaultdict

from pydantic import BaseModel as PydanticBaseModel, Field

from .node import Node
from .primitives import Rect, Vector4
from ..helpers import sort_rules_by_specificity
from ..properties import clean_value_for, default_value_for, INHERIT


class BaseModel(PydanticBaseModel):
    class Config:
        underscore_attrs_are_private = True
        arbitrary_types_allowed = True


class BoxModel(BaseModel):
    content: Rect = Field(default_factory=Rect)
    padding: Vector4 = Field(default_factory=Vector4)
    border: Vector4 = Field(default_factory=Vector4)
    margin: Vector4 = Field(default_factory=Vector4)

    @property
    def content_box(self):
        return self.content.copy()

    @property
    def padding_box(self):
        return self.content.expand_by_size(self.padding)

    @property
    def border_box(self):
        return self.padding_box.expand_by_size(self.border)

    @property
    def margin_box(self):
        return self.border_box.expand_by_size(self.margin)

    @property
    def width(self):
        return self.content.width

    @property
    def height(self):
        return self.content.height

    def copy(self):
        return self.__class__(
            content=self.content.copy(),
            padding=self.padding.copy(),
            border=self.border.copy(),
            margin=self.margin.copy(),
        )

    def __repr__(self):
        return (
            f"<BoxModel:\n"
            f"   content={self.content_box}\n"
            f"   padding={self.padding_box}\n"
            f"   border={self.border_box}\n"
            f"   margin={self.margin_box}\n"
            f">"
        )
    


class Style(BaseModel):
    values: Dict = Field(default_factory=lambda: defaultdict(dict))
    state: str = "default"

    def __getattr__(self, key):
        key = key.replace("_", "-")
        if key in self.values[self.state]:
            return self.values[self.state][key]
        if key in self.values["default"]:
            return self.values["default"][key]
        return default_value_for(key)[key]

    @classmethod
    def from_rules(cls, rules):
        style = Style()
        pseudo_rules = []
        for rule in sort_rules_by_specificity(rules):
            append_to = "default"
            if ":" in rule.selector.as_css():
                append_to = rule.selector.as_css().split(":")[1]

            for declaration in rule.declarations:
                values = [v for v in declaration.value if not v.type == "S"]
                style.values[append_to].update(
                    clean_value_for(declaration.name, *values)
                )
        return style

    def inherit_from(self, style):
        for name, value in style.values.items():
            if name in INHERIT and name not in self.values:
                self.values[name] = value

    def as_dict(self):
        return_dict = {}
        for name, value in self.values.items():
            return_dict[name] = value.as_css()
        return return_dict

    def __call__(self, parent_container):
        return CalculatedStyle(self, parent_container)


class CalculatedStyle:
    def __init__(self, style, parent_container):
        self.style = style
        self.parent_container = parent_container

    def __getattr__(self, key):
        value = getattr(self.style, key)
        if isinstance(value, (str, float, int)):
            return value
        return value.calculated_value(self.parent_container)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass


class BaseLayout(BaseModel):
    style: Style
    node: Node
    children: List["BaseLayout"] = Field(default_factory=list)
    container: BoxModel = Field(default_factory=BoxModel)

    def __iter__(self):
        return iter(self.children)
