from typing import List, Dict, Union, Optional, Any
from collections import defaultdict

from pydantic import Field, validator

from .node import Node
from .primitives import Rect, Vector4
from ..helpers import sort_rules_by_specificity
from ..properties import clean_value_for, default_value_for, INHERIT
from .base import BaseModel
from ..helpers import Dimension
from ..signals import (
    STYLE_CHANGED,
    BIND_ANIMATION,
    STOP_ANIMATION,
    ANIMATION_ENDED
)

# make the getattr play nice with blinker
EXCLUDE_ATTRS = ("im_func", "__func__")


def exit_animation(style):
    if style.animation_fill_mode != 'forwards':
        style.values["animating"] = {}
    style.animating = False


class BoxModel(BaseModel):
    content: Rect = Field(default_factory=Rect)
    padding: Vector4 = Field(default_factory=Vector4)
    border: Vector4 = Field(default_factory=Vector4)
    margin: Vector4 = Field(default_factory=Vector4)

    def reset(self):
        self.content = Rect()
        self.padding = Vector4()
        self.border = Vector4()
        self.margin = Vector4()

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
    animating: bool = False
    inherits: Optional["Style"]

    def __getattr__(self, key):
        if key in EXCLUDE_ATTRS:
            return super().__getattr__(key)
        key = key.replace("_", "-")
        if key in self.values["animating"]:
            return self.values["animating"][key]
        if key in self.values[self.state]:
            return self.values[self.state][key]
        if key in self.values["default"]:
            return self.values["default"][key]
        if self.inherits and key in INHERIT:
            return getattr(self.inherits, key)
        return default_value_for(key)[key]

    def set_state(self, state):
        if self.state == state:
            return

        previous_animation = self.animation_name
        self.state = state
        self._maybe_start_animation(previous_animation)
        STYLE_CHANGED.send(self)

    def _maybe_start_animation(self, previous_animation):
        # Move this out, ideally we send a singal that an attribute
        # (in this case the animation) changed and then pick it up 
        # somewhere else
        if self.animation_name != previous_animation:
            STOP_ANIMATION.send(self)
            self.values["animating"] = {}
            if self.animation_name != 'none':
                BIND_ANIMATION.send(self)
                self.animating = True

    def kill(self):
        STOP_ANIMATION.send(self)

    def set(self, key, value):
        key = key.replace("_", "-")
        val = getattr(self, key)
        if isinstance(val, Dimension):
            value = Dimension(value, val.unit)
        if self.animating:
            self.values["animating"][key] = value
        else:
            self.values[self.state][key] = value
        STYLE_CHANGED.send(self)

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
        # optimise this to only connect if there are animations
        ANIMATION_ENDED.connect(exit_animation)
        return style

    def inherit_from(self, style):
        self.inherits = style
        # for pseudo_class, values in style.values.items():
        #     for name, value in values.items():
        #         if name in INHERIT and name not in self.values[pseudo_class]:
        #             self.values[pseudo_class][name] = value

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
    parent: Optional[Any]

    def __iter__(self):
        return iter(self.children)

    def needs_clip(self):
        return self.style.overflow in ["hidden", "clip", "scroll", "auto"]

    def is_scrollable(self):
        if self.style.overflow not in ["scroll", "auto"]:
            return False
        if not self.is_hovering(include_children=True):
            return False
        container_bottom = self.container.content.bottom
        child_bottom = self.children[-1].container.content.bottom
        print(container_bottom < child_bottom)
        return container_bottom < child_bottom

    def is_hovering(self, include_children=False):
        is_hovering = [self.style.state == "hover"]
        if include_children:
            for child in self.children:
                is_hovering.append(child.is_hovering(include_children))
        return any(is_hovering)
