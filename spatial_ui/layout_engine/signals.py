from blinker import Signal

STYLE_CREATED = Signal("style_created")
LAYOUT_CREATED = Signal("layout_created")

LAUNCH_ANIMATION = Signal("launch_animation")
STOP_ANIMATION = Signal("stop_animation")
BIND_ANIMATION = Signal("bind_animation")
ANIMATION_ENDED = Signal("animation_ended")

STYLE_CHANGED = Signal("style_changed")
