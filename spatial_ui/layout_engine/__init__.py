from collections import defaultdict

import tinycss
from tinycss.css21 import Stylesheet
from lxml.etree import Element, SubElement

from .models.node import NodeType
from .models.primitives import Vector2
from .models.style import BoxModel, Style
from .properties import clean_value_for, default_value_for
from .layout import (
    AnonymousLayout,
    BlockLayout,
    TextLayout,
    CaretLayout,
    TableRowLayout,
    TableCellLayout,
    ScrollbarLayout,
)
from .signals import (
    STYLE_CREATED,
    LAYOUT_CREATED,
    BIND_ANIMATION,
    LAUNCH_ANIMATION,
)
from .parser.animation import load_animations


def get_layout_renderer(
    element_tree,
    css_sheet=None,
    css_file=None,
):
    if not any([css_sheet, css_file]):
        raise ValueError("A css definition is needed when rendering a layout")

    style_tree_renderer = StyleTreeRenderer.from_node_tree(
        root_node=element_tree,
        sheet=css_sheet,
        sheet_file=css_file,
    )
    return style_tree_renderer


def render_layout(
    element_tree,
    css_sheet=None,
    css_file=None,
    viewport=(0, 0)
):
    x, y = viewport
    viewport = Vector2(x=x, y=0)

    style_tree_renderer = get_layout_renderer(
        element_tree=element_tree,
        css_sheet=css_sheet,
        css_file=css_file,
    )
    style_tree = style_tree_renderer.render_layout(viewport=viewport)
    return style_tree


def _style_tree_from_node_tree(tree, node, parent=None):
    if parent is None:
        parent = Element(node.node_element_name, attrib=node.identifiers)
    else:
        parent = SubElement(parent, node.node_element_name, attrib=node.identifiers)

    tree.nodes_by_element[parent] = node
    for child in node.children:
        _style_tree_from_node_tree(tree, child, parent)

    return parent


def load_rules(sheet=None, sheet_file=None):
    # TODO: replace this by tinycss2
    if sheet_file:
        sheet = tinycss.make_parser().parse_stylesheet_file(sheet_file)
    if isinstance(sheet, str):
        sheet = tinycss.make_parser().parse_stylesheet(sheet)

    if not isinstance(sheet, Stylesheet):
        msg = "Style rules must be of type tinycss.css21.Stylesheet"
        raise ValueError(msg)
    return sheet.rules


class StyleTreeRenderer:
    def __init__(self, rules=None, animations=None):
        self.nodes_by_element = {}
        self.rules = rules
        self.animations = animations
        self._node_tree = None
        self._tree = None
        BIND_ANIMATION.connect(self._launch_animation)

    @classmethod
    def from_node_tree(cls, root_node, sheet=None, sheet_file=None):
        style_tree = cls(
            rules=load_rules(sheet, sheet_file),
            animations=load_animations(sheet, sheet_file),
        )

        root = _style_tree_from_node_tree(style_tree, root_node)
        style_tree._tree = root
        style_tree._node_tree = root_node

        return style_tree

    def render_layout(self, viewport):
        styles_by_node = self._calculate_styles()
        style_tree = self._assemble_style_tree(None, self._node_tree, styles_by_node)
        layout = AnonymousLayout()
        layout.container.content.size = viewport
        style_tree.render_layout(layout)
        return style_tree

    def _calculate_styles(self):
        rules_by_node = defaultdict(list)
        styles_by_node = defaultdict(Style)

        for rule in self.rules:
            selector = rule.selector.as_css()
            if ':' in selector:
                selector = selector.split(":")[0]
            elements = self._tree.cssselect(selector)
            for element in elements:
                node = self.nodes_by_element[element]
                rules_by_node[node].append(rule)

        for node, rules in rules_by_node.items():
            style = Style.from_rules(rules)
            style._maybe_start_animation("none")
            styles_by_node[node] = style
            STYLE_CREATED.send(style)
        return styles_by_node

    def _launch_animation(self, style):
        if style.animation_name is 'none':
            return
        sequence = self.animations[style.animation_name]
        bound_sequence = sequence.bind(style)
        LAUNCH_ANIMATION.send(bound_sequence)

    def _assemble_style_tree(self, parent, node, styles_by_node):
        style = styles_by_node[node]
        style.inherit_from(styles_by_node[parent])

        if node.node_type is NodeType.TEXT:
            layout = TextLayout(style=style, node=node, parent=parent)
        elif node.node_type is NodeType.CARET:
            layout = CaretLayout(style=style, node=node, parent=parent)
        # elif node.node_type is NodeType.SCROLLBAR:
        #     layout = ScrollbarLayout(style=style, node=node, parent=parent)
        elif style.display == 'block':
            layout = BlockLayout(style=style, node=node, parent=parent)
        elif style.display == 'table-row':
            layout = TableRowLayout(style=style, node=node, parent=parent)
        elif style.display == 'table-cell':
            layout = TableCellLayout(
                style=style,
                node=node,
                parent=parent,
                column_idx=len(parent.children)
            )
        elif style.display == 'inline':
            raise NotImplementedError()
        elif style.display == 'inline-block':
            raise NotImplementedError()
        else:
            return None

        for child in node.children:
            child_layout = self._assemble_style_tree(node, child, styles_by_node)
            if child_layout is not None:
                layout.children.append(child_layout)
        return layout

    def update_style_tree(self, style_tree, sheet):
        self.rules = load_rules(sheet=sheet)
        self.animations = load_animations(sheet=sheet)
        styles_by_node = self._calculate_styles()
        self._update_style_tree(style_tree, styles_by_node)

    def _update_style_tree(self, layout, styles_by_node):
        style = styles_by_node[layout.node]
        style.inherit_from(styles_by_node[layout.parent])
        # make the current animation stop
        layout.style._maybe_start_animation('none')
        style.set_state(layout.style.state)
        style._maybe_start_animation('none')
        layout.style = style

        for child in layout.children:
            self._update_style_tree(child, styles_by_node)
