import glfw
from OpenGL import GL
import skia
import skia as sk
from blinker import Signal

from spatial_ui.layout.css import CSSLayout
from spatial_ui.events.signals import (
    ON_HOVER,
    ON_ENTER,
    ON_EXIT,
    ON_DOWN,
    ON_DOWN,
    ON_UP,
    ON_CLICK,
    ON_FOCUS,
    ON_BLUR
)


def on_key(window, key, scancode, action, mods):
    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    # print("----")
    # print(key)
    # print(scancode)
    # print(action)
    # print(mods)


def on_char(window, unicode_num):
    print(chr(unicode_num))


class GLFWWindow:
    def __init__(self, width, height):
        self.window = None
        self.width = width
        self.height = height
        self._setup()

    def _setup(self):
        self._create_window()
        self._setup_hooks()

    def _create_window(self):
        glfw.init()
        glfw.window_hint(glfw.RESIZABLE, False)
        glfw.window_hint(glfw.VISIBLE, False)
        self.window = glfw.create_window(
            self.width, self.height, '', None, None)
        glfw.make_context_current(self.window)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    def _setup_hooks(self):
        glfw.set_key_callback(self.window, on_key)
        glfw.set_char_callback(self.window, on_char)

    def set_hover_handler(self, handler):
        glfw.set_cursor_pos_callback(self.window, handler)

    def set_button_handler(self, handler):
        glfw.set_mouse_button_callback(self.window, handler)

    def handle_events(self):
        glfw.poll_events()

    def mouse_position(self):
        glfw.get_cursor_pos(self.window)

    def commit(self):
        glfw.swap_buffers(self.window)

    def show(self):
        glfw.show_window(self.window)

    def close(self):
        glfw.set_window_should_close(self.window, True)
        glfw.terminate()

    @property
    def should_close(self):
        return glfw.window_should_close(self.window)

    def __del__(self):
        self.close()


class SkiaSurface:
    def __init__(self, width, height):
        self.surface = None
        self.context = None
        self.width = width
        self.height = height
        self._setup_context()

    def _setup_context(self):
        context = skia.GrDirectContext.MakeGL()
        backend_render_target = skia.GrBackendRenderTarget(
            width=self.width,
            height=self.height,
            sampleCnt=0,  # sampleCnt
            stencilBits=0,  # stencilBits
            glInfo=skia.GrGLFramebufferInfo(0, GL.GL_RGBA8))
        surface = skia.Surface.MakeFromBackendRenderTarget(
            context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
            skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
        assert surface is not None
        self.surface = surface
        self.context = context

    @property
    def canvas(self):
        return self.surface.getCanvas()

    def commit(self):
        self.surface.flushAndSubmit()

    def close(self):
        self.context.abandonContext()

    def __del__(self):
        self.close()


class SkiaBoxPainter:
    def __init__(self, canvas):
        self.canvas = canvas

    def draw_style_box(self, style_box):
        if self._is_simple_box(style_box):
            SkiaSimpleBoxPainter(self.canvas).draw_style_box(style_box)

        for child in style_box.children:
            self.draw_style_box(child)

    def _is_simple_box(self, style_box):
        style = style_box.style
        simple_border_width = len(set([
            style.border_top_width.value,
            style.border_left_width.value,
            style.border_bottom_width.value,
            style.border_right_width.value,
        ])) == 1
        simple_border_color = len(set([
            style.border_top_color,
            style.border_left_color,
            style.border_bottom_color,
            style.border_right_color,
        ])) == 1
        return simple_border_width and simple_border_color


class SkiaSimpleBoxPainter:
    def __init__(self, canvas):
        self.canvas = canvas
        self.paint = sk.Paint(
            AntiAlias=True
        )
        self.border_paint = sk.Paint(
            AntiAlias=True,
            Style=sk.Paint.Style.kStroke_Style
        )

    def draw_style_box(self, style_box):
        box = style_box.container.padding_box
        x, y = box.top_left.as_tuple()
        rect = sk.Rect.MakeXYWH(x, y, box.width, box.height)
        rect = self.apply_radius(rect, style_box)
        self.paint_borders(rect, style_box)
        self.paint_rect(rect, style_box)

    def apply_radius(self, rect, style_box):
        style = style_box.style
        values = [v.value for v in style.border_radius]
        radii = list(zip(
            values, values
        ))

        rrect = sk.RRect()
        rrect.setRectRadii(rect, radii)
        return rrect

    def paint_rect(self, rect, style_box):
        style = style_box.style
        self.paint.setColor(style.background_color)
        self.canvas.drawRRect(rect, self.paint)

    def paint_borders(self, rect, style_box):
        style = style_box.style
        self.border_paint.setColor(style.border_top_color)
        self.border_paint.setStrokeWidth(style.border_top_width.value * 2)
        self.canvas.drawRRect(rect, self.border_paint)



class MouseEvent:
    def __init__(self, get_element_at):
        self.current_x = None
        self.current_y = None
        self.current_hover = None
        self.current_down = None
        self.current_focus = None
        self.get_element_at = get_element_at

    def hover_handler(self, window, x, y):
        self.current_x = x
        self.current_y = y
        if ON_HOVER.receivers or ON_ENTER.receivers or ON_EXIT.receivers:
            element = self.get_element_at(x, y)
            ON_HOVER.send(element, x=x, y=y)
            if element is not self.current_hover:
                ON_ENTER.send(element)
                ON_EXIT.send(self.current_hover)
                self.current_hover = element

    def button_press_handler(self, window, button, action, mods):
        event = {
            (0, 1): self.handle_down,
            (0, 0): self.handle_up,
        }
        if ON_DOWN.receivers or ON_UP.receivers or ON_CLICK.receivers:
            element = self.get_element_at(
                x=self.current_x,
                y=self.current_y
            )
            event[(button, action)](element)

    def handle_down(self, element):
        self.current_down = element
        ON_DOWN.send(element)

    def handle_up(self, element):
        ON_UP.send(element)
        if element is self.current_down:
            ON_CLICK.send(element)
            ON_FOCUS.send(element)
            ON_BLUR.send(self.current_focus)
            self.current_focus = element
        self.current_down = None


class MouseEventGroup:
    def __init__(self, app, groups=None):
        if groups is None:
            user_events = MouseEvent(app.layout.get_node_at)
            system_events = MouseEvent(app.layout.get_element_at)
            groups = (user_events, system_events)
        self.groups = groups

    def hover_handler(self, *args, **kwargs):
        for group in self.groups:
            group.hover_handler(*args, **kwargs)

    def button_press_handler(self, *args, **kwargs):
        for group in self.groups:
            group.button_press_handler(*args, **kwargs)


def flag_hover_state(element):
    element.style.state = "hover"


def flag_active_state(element):
    element.style.state = "active"


def flag_default_state(element):
    element.style.state = "default"


class App:
    def __init__(self, width, height, **opts):
        self.window = None
        self.surface = None
        self.width = width
        self.height = height
        self._handle_opts(opts)
        self._layout_tree = None

    def _handle_opts(self, opts):
        window = opts.get('window', None)
        surface = opts.get('surface', None)
        layout = opts.get('layout', None)
        mouse_event = opts.get('mouse_event', None)
        box_painter = opts.get('box_painter', None)

        if layout is None:
            layout = None
        self.layout = layout

        if mouse_event is None:
            mouse_event = MouseEventGroup(self)
        if window is None:
            window = GLFWWindow(self.width, self.height)
            window.set_hover_handler(mouse_event.hover_handler)
            window.set_button_handler(mouse_event.button_press_handler)
        if surface is None:
            surface = SkiaSurface(self.width, self.height)
        if box_painter is None:
            box_painter = SkiaBoxPainter(surface.canvas)

        self.window = window
        self.surface = surface
        self.box_painter = box_painter

    def paint(self):
        canvas = self.surface.canvas

        self.box_painter.draw_style_box(self._layout_tree)

        self.surface.commit()
        self.window.commit()

    def setup_system_events(self, node):
        def setup_hover_handlers(element):
            ON_ENTER.connect(flag_hover_state, element)
            ON_EXIT.connect(flag_default_state, element)

        def setup_click_handlers(element):
            ON_DOWN.connect(flag_active_state, element)
            ON_UP.connect(flag_hover_state, element)

        pseudo_handlers = {
            "hover": setup_hover_handlers,
            "active": setup_click_handlers
        }

        for name in node.style.values.keys():
            if name in pseudo_handlers:
                pseudo_handlers[name](node)

        for child in node.children:
            self.setup_system_events(child)

    def run_forever(self):
        self._layout_tree = self.layout.render(self.width, self.height)
        self.setup_system_events(self._layout_tree)
        self.window.show()
        while not self.window.should_close:
            self.window.handle_events()
            self.window.mouse_position()
            self.paint()
        window.stop()

    def show(self):
        self.window.show()

    def stop(self):
        self.surface.close()
        self.window.close()


from spatial_ui.layout_engine import render_layout
from spatial_ui.layout_engine.helpers import node_tree_from_nested_struct

element_tree = node_tree_from_nested_struct(
    tuple([list(), list()])
)
css = """
list {
    width: 100px;
    height: 100px;
    background-color: red;
    border-radius: 10px 10px 10px 10px;
    border: 5px solid yellow;
    margin: 30px;
    padding: 10px;
}
list:hover {
    background-color: green;
}
list:active {
    width: 50px;
    height: 50px;
    background-color: blue;
}
"""


layout = CSSLayout(css)
layout.set_element_tree(tuple([list(), list()]))
window = App(width=500, height=500, layout=layout)



# label = Label("Input something")
# input_field = Input(placeholder="Your input")
# save = Button("Save")
# cancel = Button("cancel")

# def print_value(sender):
#     print(input_field.value)

# save.on_click(print_value)
# cancel.on_click(lambda s: window.stop())

# panel = Panel(
#     Panel(label, input_field),
#     Panel(save, cancel)
# )
# window.add(panel)
window.run_forever()
