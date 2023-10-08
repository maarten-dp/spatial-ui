from collections import defaultdict

import cssselect

from .models.node import Node, NodeType

AUTO = 'auto'

PRECENTAGE = '%'
PIXEL = 'px'
SECONDS = 's'

UNITS = [
    PRECENTAGE,
    PIXEL,
    SECONDS,
]

HORIZONTAL = 'horizontal'
VERTICAL = 'vertical'


HORIZONTAL_CANDIDATES = [
    'width',
    'left',
    'right'
]
VERTICAL_CANDIDATES = [
    'height',
    'top',
    'bottom'
]


def node_factory(element):
    node_type = NodeType.ELEMENT
    if isinstance(element, str):
        node_type = NodeType.TEXT

    kwargs = {
        'node_type': node_type,
        'node_element_name': element.__class__.__name__,
        'raw_content': element
    }
    if hasattr(element, 'name'):
        kwargs['node_class'] = element.name

    node = Node(**kwargs)
    return node


def node_tree_from_nested_struct(nested_struct, factory=node_factory):
    root = factory(nested_struct)
    # if isinstance(nested_struct, (list, set, tuple)):
    if not isinstance(nested_struct, str):
        for element in nested_struct:
            root.add(node_tree_from_nested_struct(element, factory))
    return root


def orientation_from_property_name(property_name):
    for candidate in HORIZONTAL_CANDIDATES:
        if candidate in property_name:
            return HORIZONTAL
    for candidate in VERTICAL_CANDIDATES:
        if candidate in property_name:
            return VERTICAL


def parse_value(value, unit):
    try:
        value = float(value)
    except ValueError:
        if PRECENTAGE in value:
            value = float(value.replace(PRECENTAGE, ''))
            unit = PRECENTAGE
        elif PIXEL in value:
            value = float(value.replace(PIXEL, ''))
            unit = PIXEL
        else:
            raise ValueError(f"{value} is not a valid dimension")
    if unit is None:
        unit = PIXEL
    return value, unit


def sort_rules_by_specificity(rules):
    # Sorts the rules from less important to most important
    selectors_by_importance = defaultdict(list)
    all_rules = {r.selector.as_css(): r for r in rules}

    for selector, rule in all_rules.items():
        parsed_selector, = cssselect.parse(selector)
        # parsed_selector => (most important int, int, least important int)
        importance = int("".join([str(s) for s in parsed_selector.specificity()]))
        selectors_by_importance[importance].append(selector)

    for importance in sorted(selectors_by_importance.keys()):
        selectors = selectors_by_importance[importance]
        if len(selectors) == 1:
            yield all_rules[selectors[0]]
        rules = [all_rules[s] for s in selectors]
        for rule in sorted(rules, key=lambda r: r.line):
            yield rule


class Dimension:
    def __init__(self, value, unit=None):
        value, unit = parse_value(value, unit)
        self.value = value
        if unit not in UNITS:
            raise ValueError(f'Unit "{unit}" not supported')
        self.unit = unit

    def calculated_value(self, container=None):
        if self.unit == PIXEL:
            return self.value
        if self.unit == PRECENTAGE:
            if container is None:
                raise ValueError(
                    "A container is needed to calculate percentages"
                )
            return container.width * (self.value / 100)

    def used_value(self, container=None):
        return self.calculated_value(container)

    def __repr__(self):
        return f"<Dimension ({self.value}{self.unit})>"
