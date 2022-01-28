import os.path as osp

from ..layout_engine import render_layout
from ..layout_engine.helpers import node_tree_from_nested_struct


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
                element = found_element
        return element



class CSSLayout:
    def __init__(self, css_sheet):
        self.css_sheet = css_sheet
        self.element_tree = []
        self.style_tree = None

    @classmethod
    def from_filepath(cls, file_path):
        return cls(read_file(file_path))

    def get_element_at(self, x, y):
        return get_element_at(self.style_tree, x, y)

    def get_node_at(self, x, y):
        element = get_element_at(self.style_tree, x, y)
        if element:
            return element.node.raw_content

    def set_element_tree(self, element_tree):
        self.element_tree = node_tree_from_nested_struct(element_tree)

    def render(self, width, height):
        self.style_tree = render_layout(
            element_tree=self.element_tree,
            css_sheet=self.css_sheet,
            viewport=(width, height)
        )
        return self.style_tree
