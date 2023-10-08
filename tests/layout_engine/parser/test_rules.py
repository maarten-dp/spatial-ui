import tinycss

from spatial_ui.layout_engine.models.value import QuantifiedValue
from spatial_ui.layout_engine.parser.rules import (
    _sanitize_value,
    parse_rule,
    QuantifiedValue,
)


def test_it_can_sanitize_to_a_quantified_value():
    parser = tinycss.make_parser()
    sheet = parser.parse_stylesheet("""
        .some-class{
            some-property: 25px;
        }
    """)
    value = sheet.rules[0].declarations[0].value[0]
    result = _sanitize_value(value)
    assert isinstance(result, QuantifiedValue)
    assert result.value == 25
    assert result.unit == "px"


def test_it_can_sanitize_an_ident_to_a_color():
    parser = tinycss.make_parser()
    sheet = parser.parse_stylesheet("""
        .some-class{
            some-property: blue;
        }
    """)
    value = sheet.rules[0].declarations[0].value[0]
    result = _sanitize_value(value)
    assert result == 0xff0000ff


def test_it_can_sanitize_a_hash_to_a_color():
    parser = tinycss.make_parser()
    sheet = parser.parse_stylesheet("""
        .some-class{
            some-property: #0000FF;
        }
    """)
    value = sheet.rules[0].declarations[0].value[0]
    result = _sanitize_value(value)
    assert result == 0xff0000ff


def test_it_can_sanitize_a_default_value():
    parser = tinycss.make_parser()
    sheet = parser.parse_stylesheet("""
        .some-class{
            some-property: some_value;
        }
    """)
    value = sheet.rules[0].declarations[0].value[0]
    result = _sanitize_value(value)
    assert result == "some_value"


def test_it_can_parse_non_unpackable_rule():
    parser = tinycss.make_parser()
    sheet = parser.parse_stylesheet("""
        .some-class{
            some-property: some_value;
        }
    """)
    declaration = sheet.rules[0].declarations[0]

    assert parse_rule(declaration.name, *declaration.value) == {
        "some-property": "some_value"
    }


def test_it_can_parse_an_unpackable_rule():
    parser = tinycss.make_parser()
    sheet = parser.parse_stylesheet("""
        .some-class{
            padding: 5px;
        }
    """)
    declaration = sheet.rules[0].declarations[0]

    assert parse_rule(declaration.name, *declaration.value) == {
        "padding-top": QuantifiedValue(5, "px"),
        "padding-right": QuantifiedValue(5, "px"),
        "padding-bottom": QuantifiedValue(5, "px"),
        "padding-left": QuantifiedValue(5, "px"),
    }


def test_it_can_parse_a_nested_unpackable_rule():
    parser = tinycss.make_parser()
    sheet = parser.parse_stylesheet("""
        .some-class{
            border: 5px solid black;
        }
    """)
    declaration = sheet.rules[0].declarations[0]

    assert parse_rule(declaration.name, *declaration.value) == {
        "border-top-width": QuantifiedValue(5, "px"),
        "border-top-style": "solid",
        "border-top-color": 0xff000000,
        "border-right-width": QuantifiedValue(5, "px"),
        "border-right-style": "solid",
        "border-right-color": 0xff000000,
        "border-bottom-width": QuantifiedValue(5, "px"),
        "border-bottom-style": "solid",
        "border-bottom-color": 0xff000000,
        "border-left-width": QuantifiedValue(5, "px"),
        "border-left-style": "solid",
        "border-left-color": 0xff000000,
    }


def test_it_can_parse_a_partial_unpackable_rule():
    parser = tinycss.make_parser()
    sheet = parser.parse_stylesheet("""
        .some-class{
            border: 5px solid;
        }
    """)
    declaration = sheet.rules[0].declarations[0]

    assert parse_rule(declaration.name, *declaration.value) == {
        "border-top-width": QuantifiedValue(5, "px"),
        "border-top-style": "solid",
        "border-right-width": QuantifiedValue(5, "px"),
        "border-right-style": "solid",
        "border-bottom-width": QuantifiedValue(5, "px"),
        "border-bottom-style": "solid",
        "border-left-width": QuantifiedValue(5, "px"),
        "border-left-style": "solid",
    }
