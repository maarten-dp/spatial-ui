import os.path as osp

from spatial_ui.window import App
from spatial_ui.elements import Panel, Input
from spatial_ui.layout.css import CSSLayout


css_file = osp.join(osp.abspath(osp.dirname(__file__)), "3-input.css")
layout = CSSLayout.from_filepath(css_file, observe=True)
window = App(width=500, height=500, layout=layout)

panel = Panel(
    Input(placeholder="Don't mind me, just holding this place")
)

layout.set_element_tree(panel)
window.run_forever()