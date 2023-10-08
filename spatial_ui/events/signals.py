from blinker import Signal


ON_CLICK = Signal("on_click")
ON_DOWN = Signal("on_down")
ON_UP = Signal("on_up")

ON_CHAR = Signal("on_char")
ON_BACKSPACE_KEY = Signal("on_backspace_key")
ON_ENTER_KEY = Signal("on_enter_key")
ON_ARROW_KEY = Signal("on_arrow_key")

ON_HOVER = Signal("on_hover")
ON_ENTER = Signal("on_enter")
ON_EXIT = Signal("on_exit")

ON_FOCUS = Signal("on_focus")
ON_BLUR = Signal("on_blur")

ON_FRAME = Signal("on_frame")
