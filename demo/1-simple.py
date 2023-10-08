import os.path as osp

from spatial_ui.window import App
from spatial_ui.elements import Button, Panel
from spatial_ui.layout.css import CSSLayout


css_file = osp.join(osp.abspath(osp.dirname(__file__)), "1-simple.css")
layout = CSSLayout.from_filepath(css_file, observe=True)
window = App(width=500, height=500, layout=layout)

panel = Panel(
    Button("Test"),
    Button("qfsdf qdsfq sdfq sdfqsd fq sdfq sdf qsdf qsdf qf qsdf sdf dsf"),
)

layout.set_element_tree(panel)
window.run_forever()
