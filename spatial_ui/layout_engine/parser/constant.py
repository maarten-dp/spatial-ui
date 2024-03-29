from ..models.value import QuantifiedValue


INHERIT = [
    'azimuth',
    'border-collapse',
    'border-spacing',
    'caption-side',
    'color',
    'cursor',
    'direction',
    'elevation',
    'empty-cells',
    'font-family',
    'font-size',
    'font-style',
    'font-variant',
    'font-weight',
    'font',
    'letter-spacing',
    'line-height',
    'list-style-image',
    'list-style-position',
    'list-style-type',
    'list-style',
    'orphans',
    'pitch-range',
    'pitch',
    'quotes',
    'richness',
    'speak-header',
    'speak-numeral',
    'speak-punctuation',
    'speak',
    'speech-rate',
    'stress',
    'text-align',
    'text-indent',
    'text-transform',
    'visibility',
    'voice-family',
    'volume',
    'white-space',
    'widows',
    'word-spacing',
]

COLORS = {
    "transparent": 0x00000000,
    "black": 0xff000000,
    "silver": 0xffC0C0C0,
    "gray": 0xff808080,
    "white": 0xffffffff,
    "maroon": 0xff800000,
    "red": 0xffff0000,
    "purple": 0xff800080,
    "fuchsia": 0xffff00ff,
    "green": 0xff008000,
    "lime": 0xff00ff00,
    "olive": 0xff808000,
    "yellow": 0xffffff00,
    "navy": 0xff000080,
    "blue": 0xff0000ff,
    "teal": 0xff008080,
    "aqua": 0xff00ffff,
    "aliceblue": 0xfff0f8ff,
    "antiquewhite": 0xfffaebd7,
    "aqua": 0xff00ffff,
    "aquamarine": 0xff7fffd4,
    "azure": 0xfff0ffff,
    "beige": 0xfff5f5dc,
    "bisque": 0xffffe4c4,
    "black": 0xff000000,
    "blanchedalmond": 0xffffebcd,
    "blue": 0xff0000ff,
    "blueviolet": 0xff8a2be2,
    "brown": 0xffa52a2a,
    "burlywood": 0xffdeb887,
    "cadetblue": 0xff5f9ea0,
    "chartreuse": 0xff7fff00,
    "chocolate": 0xffd2691e,
    "coral": 0xffff7f50,
    "cornflowerblue": 0xff6495ed,
    "cornsilk": 0xfffff8dc,
    "crimson": 0xffdc143c,
    "cyan": 0xff00ffff,
    "darkblue": 0xff00008b,
    "darkcyan": 0xff008b8b,
    "darkgoldenrod": 0xffb8860b,
    "darkgray": 0xffa9a9a9,
    "darkgreen": 0xff006400,
    "darkgrey": 0xffa9a9a9,
    "darkkhaki": 0xffbdb76b,
    "darkmagenta": 0xff8b008b,
    "darkolivegreen": 0xff556b2f,
    "darkorange": 0xffff8c00,
    "darkorchid": 0xff9932cc,
    "darkred": 0xff8b0000,
    "darksalmon": 0xffe9967a,
    "darkseagreen": 0xff8fbc8f,
    "darkslateblue": 0xff483d8b,
    "darkslategray": 0xff2f4f4f,
    "darkslategrey": 0xff2f4f4f,
    "darkturquoise": 0xff00ced1,
    "darkviolet": 0xff9400d3,
    "deeppink": 0xffff1493,
    "deepskyblue": 0xff00bfff,
    "dimgray": 0xff696969,
    "dimgrey": 0xff696969,
    "dodgerblue": 0xff1e90ff,
    "firebrick": 0xffb22222,
    "floralwhite": 0xfffffaf0,
    "forestgreen": 0xff228b22,
    "fuchsia": 0xffff00ff,
    "gainsboro": 0xffdcdcdc,
    "ghostwhite": 0xfff8f8ff,
    "gold": 0xffffd700,
    "goldenrod": 0xffdaa520,
    "gray": 0xff808080,
    "green": 0xff008000,
    "greenyellow": 0xffadff2f,
    "grey": 0xff808080,
    "honeydew": 0xfff0fff0,
    "hotpink": 0xffff69b4,
    "indianred": 0xffcd5c5c,
    "indigo": 0xff4b0082,
    "ivory": 0xfffffff0,
    "khaki": 0xfff0e68c,
    "lavender": 0xffe6e6fa,
    "lavenderblush": 0xfffff0f5,
    "lawngreen": 0xff7cfc00,
    "lemonchiffon": 0xfffffacd,
    "lightblue": 0xffadd8e6,
    "lightcoral": 0xfff08080,
    "lightcyan": 0xffe0ffff,
    "lightgoldenrodyellow": 0xfffafad2,
    "lightgray": 0xffd3d3d3,
    "lightgreen": 0xff90ee90,
    "lightgrey": 0xffd3d3d3,
    "lightpink": 0xffffb6c1,
    "lightsalmon": 0xffffa07a,
    "lightseagreen": 0xff20b2aa,
    "lightskyblue": 0xff87cefa,
    "lightslategray": 0xff778899,
    "lightslategrey": 0xff778899,
    "lightsteelblue": 0xffb0c4de,
    "lightyellow": 0xffffffe0,
    "lime": 0xff00ff00,
    "limegreen": 0xff32cd32,
    "linen": 0xfffaf0e6,
    "magenta": 0xffff00ff,
    "maroon": 0xff800000,
    "mediumaquamarine": 0xff66cdaa,
    "mediumblue": 0xff0000cd,
    "mediumorchid": 0xffba55d3,
    "mediumpurple": 0xff9370db,
    "mediumseagreen": 0xff3cb371,
    "mediumslateblue": 0xff7b68ee,
    "mediumspringgreen": 0xff00fa9a,
    "mediumturquoise": 0xff48d1cc,
    "mediumvioletred": 0xffc71585,
    "midnightblue": 0xff191970,
    "mintcream": 0xfff5fffa,
    "mistyrose": 0xffffe4e1,
    "moccasin": 0xffffe4b5,
    "navajowhite": 0xffffdead,
    "navy": 0xff000080,
    "oldlace": 0xfffdf5e6,
    "olive": 0xff808000,
    "olivedrab": 0xff6b8e23,
    "orange": 0xffffa500,
    "orangered": 0xffff4500,
    "orchid": 0xffda70d6,
    "palegoldenrod": 0xffeee8aa,
    "palegreen": 0xff98fb98,
    "paleturquoise": 0xffafeeee,
    "palevioletred": 0xffdb7093,
    "papayawhip": 0xffffefd5,
    "peachpuff": 0xffffdab9,
    "peru": 0xffcd853f,
    "pink": 0xffffc0cb,
    "plum": 0xffdda0dd,
    "powderblue": 0xffb0e0e6,
    "purple": 0xff800080,
    "red": 0xffff0000,
    "rosybrown": 0xffbc8f8f,
    "royalblue": 0xff4169e1,
    "saddlebrown": 0xff8b4513,
    "salmon": 0xfffa8072,
    "sandybrown": 0xfff4a460,
    "seagreen": 0xff2e8b57,
    "seashell": 0xfffff5ee,
    "sienna": 0xffa0522d,
    "silver": 0xffc0c0c0,
    "skyblue": 0xff87ceeb,
    "slateblue": 0xff6a5acd,
    "slategray": 0xff708090,
    "slategrey": 0xff708090,
    "snow": 0xfffffafa,
    "springgreen": 0xff00ff7f,
    "steelblue": 0xff4682b4,
    "tan": 0xffd2b48c,
    "teal": 0xff008080,
    "thistle": 0xffd8bfd8,
    "tomato": 0xffff6347,
    "turquoise": 0xff40e0d0,
    "violet": 0xffee82ee,
    "wheat": 0xfff5deb3,
    "white": 0xffffffff,
    "whitesmoke": 0xfff5f5f5,
    "yellow": 0xffffff00,
    "yellowgreen": 0xff9acd32,

}

DEFAULT_PROPERTY_VALUES = {
    # Unpacked by background
    "background-attachment": "scroll", 
    "background-color": COLORS["transparent"], 
    "background-image": "none", 
    "background-position": "0% 0%", 
    "background-repeat": "repeat", 

    "border-collapse": "separate",
    "border-spacing": QuantifiedValue(0, 'px'),

    # "border": "see" individual properties, 

    # "border-color": "see" individual properties, 
    "border-top-color": COLORS["transparent"],
    "border-right-color": COLORS["transparent"],
    "border-bottom-color": COLORS["transparent"],
    "border-left-color": COLORS["transparent"],

    # "border-style": "see" individual properties,
    "border-top-style": "none",
    "border-right-style": "none",
    "border-bottom-style": "none",
    "border-left-style": "none", 
    

    # "border-width": "see" individual properties, 
    "border-top-width": QuantifiedValue(0, 'px'),
    "border-right-width": QuantifiedValue(0, 'px'),
    "border-bottom-width": QuantifiedValue(0, 'px'),
    "border-left-width": QuantifiedValue(0, 'px'),

    "border-radius": (
        QuantifiedValue(0, 'px'),
        QuantifiedValue(0, 'px'),
        QuantifiedValue(0, 'px'),
        QuantifiedValue(0, 'px')
    ),

    # "font": "see" individual properties, 
    "font-family": "arial", 
    "font-size": QuantifiedValue(16, 'px'), 
    "font-style": "normal", 
    "font-variant": "normal", 
    "font-weight": "normal",
    "line-height": QuantifiedValue(0, 'px'), 

    # "padding": "see" individual properties, 
    "padding-top": QuantifiedValue(0, 'px'),
    "padding-right": QuantifiedValue(0, 'px'),
    "padding-bottom": QuantifiedValue(0, 'px'),
    "padding-left": QuantifiedValue(0, 'px'),

    # "margin": "see" individual properties, 
    "margin-right": QuantifiedValue(0, 'px'),
    "margin-left": QuantifiedValue(0, 'px'),
    "margin-top": QuantifiedValue(0, 'px'),
    "margin-bottom": QuantifiedValue(0, 'px'),

    # "outline": "see" individual properties, 
    "outline-color": "invert", 
    "outline-style": "none", 
    "outline-width": QuantifiedValue(0, 'px'), 

    "top": "auto", 
    "right": "auto", 
    "bottom": "auto", 
    "left": "auto", 

    "width": "auto", 
    "height": "auto", 
    "max-height": "none", 
    "max-width": "none", 
    "min-height": QuantifiedValue(0, 'px'),
    "min-width": QuantifiedValue(0, 'px'),
    "overflow": "visible", 
    "position": "static", 

    "clear": "none", 
    "float": "none",

    "vertical-align": "baseline", 

    "color": COLORS["white"], 
    "content": "normal", 
    "cursor": "auto", 
    "display": "block", 
    "visibility": "visible", 
    "z-index": "auto", 

    # CURRENTLY UNSUPPORTED

    # "azimuth": "center",
    # "caption-side": "top", 
    # "clip": "auto", 
    # "counter-increment": "none", 
    # "counter-reset": "none", 
    # "cue-after": "none", 
    # "cue-before": "none", 
    # "cue": "see" individual properties, 
    # "list-style-image": "none", 
    # "list-style-position": "outside", 
    # "list-style-type": "disc", 
    # "list-style": "see" individual properties, 
    # "pause-after": "0",
    # "pause-before": "0"
    # "pause": "see" individual properties, 
    # "direction": "ltr", 
    # "elevation": "level", 
    # "empty-cells": "show", 
    # "letter-spacing": "normal", 
    # "orphans": "2"
    # "page-break-after": "auto", 
    # "page-break-before": "auto", 
    # "page-break-inside": "auto", 
    # "pitch-range": "50"
    # "pitch": "medium", 
    # "play-during": "auto", 
    # "quotes": "depends" on user agent, 
    # "richness": "50"
    # "speak-header": "once", 
    # "speak-numeral": "continuous", 
    # "speak-punctuation": "none", 
    # "speak": "normal", 
    # "speech-rate": "medium", 
    # "stress": "50"
    # "table-layout": "auto", 
    # "text-align": "a" nameless value that acts as "left": "if" "direction": "is" "ltr", "right": "if" "direction": "is" "rtl": "
    # "text-decoration": "none", 
    # "text-indent": "0"
    # "text-transform": "none", 
    # "unicode-bidi": "normal", 
    # "voice-family": "depends" on user agent, 
    # "volume": "medium", 
    # "white-space": "normal", 
    # "widows": "2"
    # "word-spacing": "normal", 
}
