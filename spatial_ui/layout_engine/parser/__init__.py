import os.path as osp

import tinycss
from cssselect import parser

from .rules import parse_rule
from ..models.rules import RuleSet


def to_stylesheet(raw_sheet):
    parser = tinycss.make_parser()

    try:
        if osp.exists(raw_sheet):
            sheet = parser.parse_stylesheet_file(raw_sheet)
        else:
            sheet = parser.parse_stylesheet(raw_sheet)
    except Exception as e:
        msg = f"Sheet must be a file, filepath or raw text: {e}"
        raise ValueError(msg)
    return sheet


class StyleSheetParser:
    def __init__(self, rule_parser=None):
        if rule_parser is None:
            rule_parser = parse_rule
        self.rule_parser = rule_parser

    def parse(self, sheet):
        stylesheet = to_stylesheet(sheet)
        rule_sets = {}

        for rule in stylesheet.rules:
            values = {}
            for declaration in rule.declarations:
                parsed = self.rule_parser(declaration.name, *declaration.value)
                values.update(parsed)

            for selector in parser.parse(rule.selector.as_css()):
                rule_set = RuleSet(selector.canonical(), selector, values)
                rule_sets[rule_set.canonical] = rule_set
        return rule_sets
