import pytest

from spatial_ui.layout_engine.parser import StyleSheetParser
from spatial_ui.layout_engine.models.rules import RuleSet, StyleRules


def test_it_can_parse_ruleset():
    ruleset = """
        div {
          color: blue;
        }
    """
    parser = StyleSheetParser()
    rule_sets = parser.parse(ruleset)

    assert len(rule_sets) == 1
    assert rule_sets["div"].values == {
        "color": 0xff0000ff,
    }


def test_it_can_parse_multiple_rulesets():
    ruleset = """
        div {
          color: blue;
        }
        p {
          color: green;
        }
    """
    parser = StyleSheetParser()
    rule_sets = parser.parse(ruleset)

    assert len(rule_sets) == 2
    assert rule_sets["div"].values == {
        "color": 0xff0000ff,
    }
    assert rule_sets["p"].values == {
        "color": 0xff008000,
    }


def test_it_can_parse_multiple_inline_rulesets():
    ruleset = """
        div, p {
          color: blue;
        }
    """
    parser = StyleSheetParser()
    rule_sets = parser.parse(ruleset)

    assert len(rule_sets) == 2
    assert rule_sets["div"].values == {
        "color": 0xff0000ff,
    }
    assert rule_sets["p"].values == {
        "color": 0xff0000ff,
    }


def test_it_can_get_a_value_from_the_highest_specificity():
    ruleset = """
        div {
          color: blue;
        }
        div .test {
          color: green;
        }
    """
    parser = StyleSheetParser()
    rule_sets = parser.parse(ruleset)

    style_rule = StyleRules()
    style_rule.rule_sets.extend(rule_sets.values())
    style_rule.sort()

    assert style_rule.color == 0xff008000


def test_it_can_get_a_value_from_the_highest_specificity():
    ruleset = """
        div {
          color: blue;
        }
        div .test {
          color: green;
        }
    """
    parser = StyleSheetParser()
    rule_sets = parser.parse(ruleset)

    style_rule = StyleRules()
    style_rule.rule_sets.extend(rule_sets.values())
    style_rule.sort()

    assert style_rule.color == 0xff008000


def test_it_can_get_the_next_value_if_not_found_on_the_highest_specificity():
    ruleset = """
        div {
          color: blue;
        }
        div .test {
          background-color: green;
        }
    """
    parser = StyleSheetParser()
    rule_sets = parser.parse(ruleset)

    style_rule = StyleRules()
    style_rule.add_rule_sets(rule_sets.values())

    assert style_rule.color == 0xff0000ff


def test_it_can_fallback_to_the_default_values():
    ruleset = """
        div {
          background-color: blue;
        }
    """
    parser = StyleSheetParser()
    rule_sets = parser.parse(ruleset)

    style_rule = StyleRules()
    style_rule.add_rule_sets(rule_sets.values())

    assert style_rule.color == 0xffffffff


def test_it_raises_an_attribute_error_when_accessing_a_non_existing_attribute():
    style_rule = StyleRules()

    with pytest.raises(AttributeError):
        style_rule.does_not_exist
