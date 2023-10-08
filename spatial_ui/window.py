import os
import os.path as osp
import psutil
from contextlib import contextmanager
from statistics import mean

import glfw
from OpenGL import GL
import skia
import skia as sk
from blinker import Signal
import time

from spatial_ui.layout_engine.models.node import NodeType
from spatial_ui.layout_engine.layout.misc import ScrollbarLayout

from spatial_ui.layout.css import CSSLayout
from spatial_ui.elements.primitives.element import Element
from spatial_ui.events.signals import (
    ON_HOVER,
    ON_ENTER,
    ON_EXIT,
    ON_DOWN,
    ON_UP,
    ON_CLICK,
    ON_FOCUS,
    ON_BLUR,
    ON_FRAME,
    ON_CHAR,
    ON_BACKSPACE_KEY,
    ON_ENTER_KEY,
    ON_ARROW_KEY,
)

SHOW_FPS = True
SHOW_CONTAINER = False
ARROWS = {
    glfw.KEY_RIGHT: "right",
    glfw.KEY_LEFT: "left",
    glfw.KEY_DOWN: "down",
    glfw.KEY_UP: "up",
}


def on_key(window, key, scancode, action, mods):
    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    if key == glfw.KEY_BACKSPACE and action == 1:
        ON_BACKSPACE_KEY.send()
    if key == glfw.KEY_ENTER and action == 1:
        ON_ENTER_KEY.send()
    if key in ARROWS and action == 1:
        ON_ARROW_KEY.send(ARROWS[key])
    if (key, action, mods) == (49, 1, 2):
        global SHOW_FPS
        SHOW_FPS = not SHOW_FPS
    if (key, action, mods) == (50, 1, 2):
        global SHOW_CONTAINER
        SHOW_CONTAINER = not SHOW_CONTAINER
        if SHOW_CONTAINER:
            glfw.set_window_size(window, 850, 500)
        else:
            glfw.set_window_size(window, 500, 500)

def on_char(window, unicode_num):
    ON_CHAR.send(chr(unicode_num))


class GLFWWindow:
    def __init__(self, width, height):
        self.window = None
        self.width = width
        self.height = height
        self.last_time = glfw.get_time()
        self._current_delta = 0
        self._setup()

    def _setup(self):
        self._create_window()
        self._setup_hooks()
        # uncomment to disable 60fps
        # glfw.swap_interval(0)

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

    def resize(self, width, height):
        glfw.set_window_size(self.window, width, height)

    def show(self):
        glfw.show_window(self.window)

    def close(self):
        glfw.set_window_should_close(self.window, True)
        glfw.terminate()

    def get_delta(self):
        current_time = glfw.get_time()
        delta = current_time - self.last_time
        self.last_time = current_time
        self._current_delta = delta
        return delta

    @property
    def should_close(self):
        return glfw.window_should_close(self.window)

    def __del__(self):
        self.close()


class SkiaSurface:
    def __init__(self, width, height, background_color=0xff303030):
        self.surface = None
        self.context = None
        self.width = width
        self.height = height
        self.background_color = background_color
        self._setup_context()

    def _setup_context(self):
        context = skia.GrDirectContext.MakeGL()
        backend_render_target = skia.GrBackendRenderTarget(
            width=self.width + 350,
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

    def clear(self):
        self.surface.getCanvas().clear(self.background_color)

    @property
    def canvas(self):
        return self.surface.getCanvas()

    def commit(self):
        self.surface.flushAndSubmit()

    def close(self):
        self.context.abandonContext()

    def __del__(self):
        self.close()


FONT_PAINT = {}
TYPEFACE = {}

def get_font_paint(color):
    if color in FONT_PAINT:
        return FONT_PAINT[color]
    paint = skia.Paint(Color=color, AntiAlias=True)
    FONT_PAINT[color] = paint
    return paint


def get_typeface(path):
    if path in TYPEFACE:
        return TYPEFACE[path]
    font = skia.Typeface.MakeFromFile(path)
    TYPEFACE[path] = font
    return font


@contextmanager
def clip(canvas, box):
    rect = sk.Rect.MakeXYWH(box.x, box.y, box.width, box.height)
    canvas.save()
    canvas.clipRect(rect)
    yield
    canvas.restore()


class SkiaBoxPainter:
    def __init__(self, canvas):
        self.canvas = canvas
        self.simple_box_painter = SkiaSimpleBoxPainter(self.canvas)

    def draw_style_box(self, style_box):
        if self._is_simple_box(style_box):
            self.simple_box_painter.draw_style_box(style_box)

        for child in style_box.children:
            if style_box.needs_clip():
                with clip(self.canvas, style_box.container.content):
                    self._draw_child(child, style_box)
            else:
                self._draw_child(child, style_box)
        if style_box.is_scrollable():
            print("drawing scrollbar")
            self.draw_scrollbar(style_box)

    def _draw_child(self, child, parent):
        if child.style.display == "none":
            return
        if child.node.node_type == NodeType.ELEMENT:
            self.draw_style_box(child)
        elif child.node.node_type == NodeType.CARET:
            caret_index = parent.node.raw_content._index
            text_sibling = [c for c in parent.children if c.node.node_type == NodeType.TEXT][0]
            x_offset = text_sibling._get_x_offset(caret_index)
            child.container.content.x = parent.container.content.x + x_offset
            self.draw_style_box(child)
        elif child.node.node_type == NodeType.SCROLLBAR:
            self.draw_style_box(child)
        elif child.node.node_type == NodeType.PLACEHOLDER:
            if child.parent.raw_content.must_draw:
                self.draw_text(child.children[0])
        elif child.node.node_type == NodeType.TEXT:
            self.draw_text(child)
        else:
            raise ValueError("Unknown NodeType {child.node.node_type}")

    def draw_scrollbar(self, parent_box):
        print("drawing scrollbar")
        # layout = ScrollbarLayout().render_layout(parent_box)
        # self._draw_child(layout, parent)

    def draw_text(self, child):
        # font_paint = skia.Paint(Color=child.style.color, AntiAlias=True)
        font_paint = get_font_paint(child.style.color)
        for text_line in child.text_blocks:
            # typeface = skia.Typeface.MakeFromFile(text_line.font.path)
            typeface = get_typeface(text_line.font.path)
            font = skia.Font(typeface, text_line.font.size)
            font.setEdging(skia.Font.Edging.kAntiAlias)
            self.canvas.drawString(
                text=text_line.text,
                x=text_line.box.left,
                y=text_line.box.bottom,
                font=font,
                paint=font_paint,
            )

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


class DiagnosticPainter:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.fps_history = []
        self.x = x
        self.y = y
        self.font_paint = get_font_paint(0xff000000)
        self.border_paint = paint = skia.Paint(
            Color=0xffffffff,
            AntiAlias=True,
            Style=sk.Paint.Style.kStroke_Style,
            StrokeWidth=5.0,
        )
        self.process = psutil.Process(os.getpid())

    def draw(self, fps):
        self.draw_fps(fps)
        self.draw_memory()

    def draw_fps(self, fps):
        self.fps_history.append(fps)
        if len(self.fps_history) > 60:
            self.fps_history.pop(0)
        fps = int(mean(self.fps_history))
        self.draw_text(f"{fps} fps", line=0)

    def draw_memory(self):
        suffixes = ["b", "kb", "mb", "gb"]
        memory = self.process.memory_info().rss
        suffix = suffixes.pop(0)
        while memory > 1024 and suffixes:
            memory /= 1024
            suffix = suffixes.pop(0)
        self.draw_text(f"{int(memory)} {suffix}", line=1)

    def draw_text(self, text, line):
        font = skia.Font(list(TYPEFACE.values())[0], 15)
        font.setEdging(skia.Font.Edging.kAntiAlias)
        for paint in [self.border_paint, self.font_paint]:
            self.canvas.drawString(
                text=text,
                x=self.x,
                y=self.y + (line * 17),
                font=font,
                paint=paint,
            )


class ContainerPainter:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = 500
        self.y = 0
        self.width = 350
        self.height = 500
        self.font_paint = get_font_paint(0xff000000)
        self.border_paint = skia.Paint(
            Color=0xffffffff,
            AntiAlias=True,
            Style=sk.Paint.Style.kStroke_Style,
            StrokeWidth=5.0,
        )
        self.background_paint = skia.Paint(
            Color=0xffffffff,
            AntiAlias=True,
        )
        self.content_paint = skia.Paint(
            Color=0x9900008b,
            AntiAlias=True,
        )
        self.padding_paint = skia.Paint(
            Color=0x99ff8c00,
            AntiAlias=True,
        )
        self.margin_paint = skia.Paint(
            Color=0x998b0000,
            AntiAlias=True,
        )
        self.current_hover = None
        ON_ENTER.connect(self.set_current_hover)
        ON_EXIT.connect(self.remove_current_hover)

    def set_current_hover(self, element):
        self.current_hover = element

    def remove_current_hover(self, element):
        if self.current_hover is element:
            self.current_hover = None

    def draw(self):
        self.draw_header()
        self.draw_background()
        self.draw_container()

    def draw_header(self):
        if not self.current_hover:
            self.draw_text("Hover over container", 0)

    def draw_container(self):
        if self.current_hover:
            self.draw_visuals()

            lines = []
            container = self.current_hover.container
            boxes = [
                (container.content_box, "Content"),
                (container.padding_box, "Padding"),
                (container.border_box, "Borders"),
                (container.margin_box, "Margin"),
            ]
            for box, header in boxes:
                lines.append(header)
                lines.append(f"  x: {box.x}   y: {box.y}")
                lines.append(f"  width: {box.width}")
                lines.append(f"  height: {box.height}")

            lines.append("")
            lines.append("CSS rules")
            for name, value in self.current_hover.style.values["default"].items():
                lines.append(f"  {name}: {value}")

            text = repr(self.current_hover.container).split("\n")
            for idx, part in enumerate(lines):
                self.draw_text(part, idx)

    def draw_visuals(self):
        container = self.current_hover.container
        boxes = [
            (container.margin_box, self.margin_paint, container.padding_box),
            (container.padding_box, self.padding_paint, container.content_box),
            (container.content_box, self.content_paint, None),
        ]
        for box, paint, clipping_box in boxes:
            self.draw_box(box, paint, clipping_box)

    def draw_box(self, box, paint, clip_box):
        rect = sk.Rect.MakeXYWH(box.x, box.y, box.width, box.height)
        with clip(self.canvas, box):
            if clip_box:
                clip_rect = sk.Rect.MakeXYWH(
                    clip_box.x, clip_box.y, clip_box.width, clip_box.height
                )
                self.canvas.clipRect(clip_rect, op=sk.ClipOp.kDifference)
            self.canvas.drawRect(rect, paint)

    def draw_text(self, text, line):
        font = skia.Font(list(TYPEFACE.values())[0], 15)
        font.setEdging(skia.Font.Edging.kAntiAlias)
        for paint in [self.border_paint, self.font_paint]:
            self.canvas.drawString(
                text=text,
                x=self.x + 5,
                y=self.y + 15 + (line * 17),
                font=font,
                paint=paint,
            )

    def draw_background(self):
        rect = sk.Rect.MakeXYWH(self.x, self.y, self.width, self.height)
        self.canvas.drawRect(rect, self.background_paint)


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
            if element is not self.current_focus:
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
    element.style.set_state("hover")


def flag_focus_state(element):
    element.style.set_state("focus")
    if element.node.raw_content.__class__.__name__ == "Input":
        def is_caret(n):
            return n.node.node_type == NodeType.CARET
        caret = [n for n in element.children if is_caret(n)][0]
        caret.style.set_state("focus")

def flag_active_state(element):
    element.style.set_state("active")


def flag_default_state(element):
    element.style.set_state("default")
    if element.node.raw_content.__class__.__name__ == "Input":
        def is_caret(n):
            return n.node.node_type == NodeType.CARET
        caret = [n for n in element.children if is_caret(n)][0]
        caret.style.set_state("default")


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
            # default to box layout
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
        self.diagnostic_painter = DiagnosticPainter(
            self.surface.canvas, 10, self.height - 32)
        self.container_painter = ContainerPainter(self.surface.canvas)

    def paint(self, delta):
        self.surface.clear()
        self.box_painter.draw_style_box(self._layout_tree)
        if SHOW_FPS:
            self.diagnostic_painter.draw(1 / delta)
        if SHOW_CONTAINER:
            self.container_painter.draw()

        self.surface.commit()
        self.window.commit()

    def setup_system_events(self, node):
        def setup_hover_handlers(element):
            ON_ENTER.connect(flag_hover_state, element)
            ON_EXIT.connect(flag_default_state, element)

        def setup_click_handlers(element):
            ON_DOWN.connect(flag_active_state, element)
            ON_UP.connect(flag_hover_state, element)

        def setup_focus_handlers(element):
            setup_click_handlers(element)
            ON_FOCUS.connect(flag_focus_state, element)
            ON_BLUR.connect(flag_default_state, element)

        pseudo_handlers = {
            "hover": setup_hover_handlers,
            "active": setup_click_handlers,
            "focus": setup_focus_handlers,
        }

        for name, handler in pseudo_handlers.items():
            handler(node)

        # for name in node.style.values.keys():
        #     if name in pseudo_handlers:
        #         pseudo_handlers[name](node)

        ui_element = node.node.raw_content
        if isinstance(ui_element, Element):
            ui_element.register_system_events(node)

        for child in node.children:
            self.setup_system_events(child)

    def run_forever(self):
        self._layout_tree = self.layout.render(self.width, self.height)
        self.setup_system_events(self._layout_tree)
        self.window.show()

        handle_events = self.window.handle_events
        mouse_position = self.window.mouse_position
        paint = self.paint
        delta = self.window.get_delta

        while not self.window.should_close:
            t = delta()
            handle_events()
            mouse_position()
            ON_FRAME.send(t)
            paint(t)
        window.stop()

    def show(self):
        self.window.show()

    def stop(self):
        self.surface.close()
        self.window.close()
