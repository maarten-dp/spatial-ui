from collections import defaultdict

import tinycss
from tinycss.css21 import Stylesheet
from lxml.etree import Element, SubElement

from .models.node import NodeType
from .models.primitives import Vector2
from .models.style import BoxModel, Style
from .properties import clean_value_for, default_value_for
from .layout import AnonymousLayout, BlockLayout, TextLayout


def render_layout(
    element_tree,
    css_sheet=None,
    css_file=None,
    viewport=(0, 0)
):
    if not any([css_sheet, css_file]):
        raise ValueError("A css definition is needed when rendering a layout")
    x, y = viewport
    viewport = Vector2(x=x, y=0)

    style_tree_renderer = StyleTreeRenderer.from_node_tree(
        root_node=element_tree,
        sheet=css_sheet,
        sheet_file=css_file,
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


class StyleTreeRenderer:
    def __init__(self, rules=None):
        self.nodes_by_element = {}
        self.rules = rules
        self._node_tree = None
        self._tree = None

    @classmethod
    def from_node_tree(cls, root_node, sheet=None, sheet_file=None):
        if sheet_file:
            sheet = tinycss.make_parser().parse_stylesheet_file(rules_file)
        if isinstance(sheet, str):
            sheet = tinycss.make_parser().parse_stylesheet(sheet)

        if not isinstance(sheet, Stylesheet):
            msg = "Style rules must be of type tinycss.css21.Stylesheet"
            raise ValueError(msg)

        style_tree = cls(rules=sheet.rules)

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

    def nodes_for_selector(self, css_selector):
        elements = self.tree.cssselect(css_selector)
        for element in elements:
            yield self.nodes[element]

    def  _calculate_styles(self):
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
            styles_by_node[node] = Style.from_rules(rules)
        return styles_by_node

    def _assemble_style_tree(self, parent, node, styles_by_node):
        style = styles_by_node[node]
        style.inherit_from(styles_by_node[parent])

        if node.node_type == NodeType.TEXT:
            layout = TextLayout(style=style, node=node)
        elif style.display is 'block':
            layout = BlockLayout(style=style, node=node)
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
