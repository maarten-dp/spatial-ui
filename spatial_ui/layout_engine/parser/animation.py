import tinycss2
import tinycss
from arcade_curtains import animation

from ..models.style import Style
from ..helpers import Dimension


def is_keyframe(rule):
    return rule.type == "at-rule" and rule.lower_at_keyword == "keyframes"


def get_identity(at_rule):
    return [t.serialize() for t in at_rule.prelude if t.type == "ident"][0]


def clean(content):
    return [c for c in content if c.type != "whitespace"]


def load_animations(sheet=None, sheet_file=None):
    if sheet_file:
        with open(sheet_file) as fh:
            sheet = fh.read()
    sheet = tinycss2.parse_stylesheet(
        sheet,
        skip_comments=True,
        skip_whitespace=True
    )

    animations = {}
    at_rules = [r for r in sheet if is_keyframe(r)]
    for at_rule in at_rules:
        animations[get_identity(at_rule)] = parse_animation(at_rule)
    return animations


def parse_animation(at_rule):
    parser = tinycss.make_parser()
    elements = clean(at_rule.content)
    keyframes = {}
    sequence = UnboundSequence()
    for point_in_time, definition in zip(elements[::2], elements[1::2]):
        res = parser.parse_stylesheet(f"stub {definition.serialize()}")
        values = Style.from_rules(res.rules).values["default"]
        sequence.add_keyframe(
            point_in_time=point_in_time.value / 100,
            keyframe=KeyFrame(values)
        )
    return sequence


class Sprite:
    def __init__(self, style):
        object.__setattr__(self, "style", style)

    def __setattr__(self, key, value):
        if isinstance(value, float):
            value = int(value)
        self.style.set(key, int(value))


class UnboundSequence:
    def __init__(self):
        self.keyframes = {}

    def add_keyframe(self, point_in_time, keyframe):
        self.keyframes[point_in_time] = keyframe

    def bind(self, style):
        return BoundSequence(style, self.keyframes)


class BoundSequence:
    def __init__(self, style, keyframes):
        self.sprite = Sprite(style)
        self.sequence = animation.Sequence(
            loop=style.animation_iteration_count == "infinite"
        )
        duration  = style.animation_duration.value
        for pit, keyframe in keyframes.items():
            self.sequence.add_keyframe(
                point_in_time=pit * duration,
                keyframe=keyframe
            )


class KeyFrame:
    def __init__(self, values):
        self.values = values

    def __getattr__(self, key):
        if key in self.values:
            value = self.values[key]
            if isinstance(value, Dimension):
                value = value.value
            return value
        super().__getattr__(key)

    def to_list(self):
        # Hack to have this keyframe work with sequence
        attrs = list(self.values.keys())
        animation.TRACKED_ATTRIBUTES = attrs
        return [getattr(self, attr) for attr in attrs]
