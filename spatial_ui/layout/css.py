import os.path as osp
from queue import Queue, Empty

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from arcade_curtains.animation import AnimationManager

from ..layout_engine import render_layout, get_layout_renderer
from ..layout_engine.layout import AnonymousLayout
from ..layout_engine.helpers import node_tree_from_nested_struct
from ..layout_engine.models.primitives import Vector2
from ..layout_engine.models.node import Node, NodeType
from ..layout_engine.signals import (
    STYLE_CHANGED,
    LAUNCH_ANIMATION,
    STOP_ANIMATION,
    ANIMATION_ENDED,
)
from ..elements.input import Caret, Placeholder, Text
from ..elements import Scrollbar
from ..events.signals import ON_FRAME

LAYOUT_ROOT_PATH = osp.abspath(osp.dirname(__file__))
AGENT_CSS_PATH = osp.join(LAYOUT_ROOT_PATH, "assets", "agent.css")
IGNORED_NODE_TYPES = (
    NodeType.TEXT, NodeType.CARET, NodeType.PLACEHOLDER
)


def read_file(path):
    if not osp.exists(path):
        raise ValueError(f"{path} was not found")
    with open(path, "r") as fh:
        return fh.read()


def get_element_at(element, x, y):
    # for element in reversed(tree):
    box = element.container.border_box
    if box.left <= x <= box.right and box.top <= y <= box.bottom:
        for child in element.children:
            found_element = get_element_at(child, x, y)
            if found_element:
                # currently here because we don't want to return text nodes
                # ideally we want to move this if statement when it makes sense
                if found_element.node.node_type not in IGNORED_NODE_TYPES:
                    element = found_element
        return element


def start_watchdog(layout, file_path):
    event_handler = ReloadCSSHandler(layout)
    observer = Observer()
    observer.schedule(event_handler, file_path)
    observer.start()


def node_factory(element):
    node_type = NodeType.ELEMENT
    if isinstance(element, (str, Text)):
        node_type = NodeType.TEXT
    elif isinstance(element, Caret):
        node_type = NodeType.CARET
    elif isinstance(element, Placeholder):
        node_type = NodeType.PLACEHOLDER
    elif isinstance(element, Scrollbar):
        node_type = NodeType.SCROLLBAR

    kwargs = {
        'node_type': node_type,
        'node_element_name': element.__class__.__name__,
        'raw_content': element
    }
    if hasattr(element, 'name'):
        kwargs['node_class'] = element.name

    node = Node(**kwargs)
    return node


class EventableList(list):
    def remove(self, item):
        super().remove(item)
        ANIMATION_ENDED.send(item.sprite.style)


class ReloadCSSHandler(FileSystemEventHandler):
    def __init__(self, layout):
        self.layout = layout

    def on_modified(self, event):
        if event.is_directory:
            return
        self.layout.reload(event.src_path)


class CSSLayout:
    def __init__(self, css_sheet):
        self.agent_css = read_file(AGENT_CSS_PATH)
        self.css_sheet = "\n".join([self.agent_css, css_sheet])
        self.element_tree = []
        self.style_tree = None
        self.renderer = None
        self.animation_manager = AnimationManager()
        self.animation_manager.animations = EventableList()
        self.running_animations = {}
        self.width = 0
        self.height = 0
        self.dirty = False
        STYLE_CHANGED.connect(self._flag_dirty)
        LAUNCH_ANIMATION.connect(self.register_animation)
        STOP_ANIMATION.connect(self.kill_animation)
        ON_FRAME.connect(self.animation_manager._blip)
        ON_FRAME.connect(self._refresh)

    @classmethod
    def from_filepath(cls, file_path, observe=False):
        layout = cls(read_file(file_path))
        if observe:
            start_watchdog(layout, file_path)
        return layout

    def get_element_at(self, x, y):
        return get_element_at(self.style_tree, x, y)

    def get_node_at(self, x, y):
        element = get_element_at(self.style_tree, x, y)
        if element:
            return element.node.raw_content

    def set_element_tree(self, element_tree):
        self.element_tree = node_tree_from_nested_struct(
            element_tree,
            factory=node_factory
        )

    def render(self, width, height):
        self.width = width
        self.height = height
        self.renderer = get_layout_renderer(
            element_tree=self.element_tree,
            css_sheet=self.css_sheet,
        )
        viewport = Vector2(x=width, y=0)
        self.style_tree = self.renderer.render_layout(viewport=viewport)
        return self.style_tree

    def reload(self, path):
        self.css_sheet = "\n".join([self.agent_css, read_file(path)])
        self.renderer.update_style_tree(self.style_tree, self.css_sheet)
        self.refresh(self.width, self.height)

    def _flag_dirty(self, style):
        self.dirty = True

    def _refresh(self, style):
        if self.dirty:
            self.dirty = False
            self.refresh()

    def refresh(self, width=None, height=None):
        self.width = width or self.width
        self.height = height or self.height
        layout = AnonymousLayout()
        layout.container.content.size = Vector2(x=self.width, y=0)
        self.reset_container(self.style_tree)
        self.style_tree.render_layout(layout)

    def reset_container(self, node):
        node.container.reset()
        for child in node.children:
            self.reset_container(child)

    def register_animation(self, animation):
        self.animation_manager.fire(animation.sprite, animation.sequence)
        self.running_animations[id(animation.sprite.style)] = animation.sprite

    def kill_animation(self, style):
        sprite = self.running_animations.get(id(style))
        self.animation_manager.kill(sprite)
