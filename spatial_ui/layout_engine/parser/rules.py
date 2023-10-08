# from tinycss.speedups import CToken

from ..models.value import QuantifiedValue
from .constant import COLORS


UNPACK_MAPPING = {
    "margin": [
        'margin-top',
        'margin-right',
        'margin-bottom',
        'margin-left'
    ],
    "padding": [
        'padding-top',
        'padding-right',
        'padding-bottom',
        'padding-left'
    ],
    "border": [
        'border-top',
        'border-right',
        'border-bottom',
        'border-left'
    ],
    "border-top": [
        'border-top-width',
        'border-top-style',
        'border-top-color',
    ],
    "border-right": [
        'border-right-width',
        'border-right-style',
        'border-right-color',
    ],
    "border-bottom": [
        'border-bottom-width',
        'border-bottom-style',
        'border-bottom-color',
    ],
    "border-left": [
        'border-left-width',
        'border-left-style',
        'border-left-color',
    ],
    "border-color": [
        'border-top-color',
        'border-right-color',
        'border-bottom-color',
        'border-left-color'
    ],
    "border-width": [
        'border-top-width',
        'border-right-width',
        'border-bottom-width',
        'border-left-width'
    ],
    "border-style": [
        'border-top-style',
        'border-right-style',
        'border-bottom-style',
        'border-left-style'
    ],
    "background": [
        'background-color',
        'background-image',
        'background-repeat',
        'background-attachment',
        'background-position',
    ],
    "font": [
        'font-style',
        'font-variant',
        'font-weight',
        'font-size',
        'line-height',
        'font-size',
        'font-family',
    ],
    "ouline": [
        'outline-color',
        'outline-style',
        'outline-width',
    ],
}


def _sanitize_value(value):
    if isinstance(value, CToken):
        if value.type in ("DIMENSION", "PERCENTAGE"):
            return QuantifiedValue(value.value, value.unit)
        elif value.type in ("HASH"):
            return 0xff000000 | int(value.value[1:], base=16)
        elif value.type in ("IDENT") and value.value in COLORS:
            return COLORS[value.value]
        else:
            return value.value
    return value


def parse_rule(property_name, *values):
    parsed_properties = {}
    values = [v for v in values if not v.type == "S"]

    to_unpack = UNPACK_MAPPING.get(property_name, [property_name])
    if len(values) == 1:
        values = values * len(to_unpack)


    for idx, property in enumerate(to_unpack):
        if property in UNPACK_MAPPING:
            # further unpack the property
            parsed_properties.update(parse_rule(property, *values))
        else:
            if idx < len(values):
                parsed_properties[property] = _sanitize_value(values[idx])

    return parsed_properties
