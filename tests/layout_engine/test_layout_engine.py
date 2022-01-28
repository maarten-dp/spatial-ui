import os.path as osp

import tinycss
from spatial_ui.layout_engine import render_layout
from spatial_ui.layout_engine.models.style import Style
from spatial_ui.layout_engine.helpers import node_tree_from_nested_struct

ROOT_PATH = osp.dirname(__file__)
DATA_PATH = osp.join(osp.dirname(ROOT_PATH), "data")


def test_style_rules_takes_the_highest_specificity():
    css = """
    List {
      width: 100px;
      color: red;
    }
    List #SomeId {
      width: 150px;
    }
    """

    sheet = tinycss.make_parser().parse_stylesheet(css)
    style = Style.from_rules(sheet.rules)

    assert style.as_dict() == {
        'width': '150px',
        'color': 'red'
    }


def test_style_rules_takes_the_last_defined_on_equal_specificity():
    css = """
    List {
      width: 100px;
      color: red;
    }
    Set {
      width: 150px;
    }
    """

    sheet = tinycss.make_parser().parse_stylesheet(css)
    style = Style.from_rules(sheet.rules)

    assert style.as_dict() == {
        'width': '150px',
        'color': 'red'
    }


def test_it_can_render_a_layout_on_an_element_tree():
    element_tree = node_tree_from_nested_struct(
        list([
            tuple(),
            tuple([
                set()
            ]),
            tuple([
                set(),
                set([
                    "bruh qsf sqdqgs qsgqs qfsqsd qgqsg qsf qsf qsfd qg q rg "
                    "efq zef dsqf qsf z ef ef qsdf za efa ezf  sqf qdsf qs"]),
                set()
            ])
        ])
    )
    css = """
    list {
        width: 100%;
        background-color: orange;
        margin: 5px;
        padding: 10px;
    }
    tuple {
        width: 100%;
        margin: 2px;
        min-height: 150px;
        background-color: moccasin;
        border: 2px solid peru;
        padding: 15px
    }
    set {
        width: 40%;
        height: 100px;
        margin: 5px;
        float: right;
        background-color: oldlace;
        font-size: 16px;
        line-height: 5px;
        padding: 15px;
    }
    """
    style_tree = render_layout(
        element_tree=element_tree,
        css_sheet=css,
        viewport=(1000, 1000)
    )
    import pdb; pdb.set_trace()
