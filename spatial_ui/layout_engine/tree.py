from lxml.etree import Element, SubElement

from .models.rules import StyleRules


class StylableElement:
    def __init__(self, element_type, identifier, data, tree=None):
        self.tree = tree
        self.element_type = element_type
        self.identifier = identifier
        self.style_rules = StyleRules()
        self.data = data

    def add_child(self, element_type, identifier, data):
        if self.tree is None:
            raise Exception("This element is not bound to a tree")
        self.tree.make_node(
            element_type=element_type,
            identifier=identifier,
            data=data,
            parent=self,
        )


class StylableTree:
    def __init__(self, rule_sets=None):
        self.root = Element("root")
        self.rule_sets = rule_sets
        self.elements = {}

    def render_styles(self):
        for element in self.elements.values():
            element.style_rules.rule_sets.clear()

        for rule_set in self.rule_sets:
            for element in self.root.cssselect(rule_set.canonical):
                element.style_rules.add_rule_set(rule_set)

    def make_node(self, element_type, identifier, data, parent=None):
        if identifier in self.elements:
            raise ValueError("Identifier already exists in tree")

        if parent is None:
            parent = self.root
        
        if isinstance(parent, str):
            parent = self.root.cssselect(parent)

        element = StylableElement(
            tree=self,
            element_type=element_type,
            identifier=identifier,
            data=data,
        )

        self.elements[identifier] = element
        SubElement(parent, node.__class__.__name__, id=dentifier)
