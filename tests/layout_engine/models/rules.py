from spatial_ui.layout_engine.parser import StyleSheetParser


def test_it_can_compare_on_specificity():
    ruleset = """
        div .some_class {
          color: blue;
        }
        div {
          color: green;
        }
    """
    parser = StyleSheetParser()
    rule_sets = parser.parse(ruleset)

    set1 = rule_sets["div   .some_class"]
    set2 = rule_sets["div"]
    assert set1 > set2
    assert set1 >= set2
    assert set2 < set1
    assert set2 <= set1


def test_it_can_sort_a_ruleset():
    ruleset = """
        div .some_class {
          color: blue;
        }
        div {
          color: green;
        }
    """
    parser = StyleSheetParser()
    rule_sets = parser.parse(ruleset)

    set1 = rule_sets["div   .some_class"]
    set2 = rule_sets["div"]
    assert sorted([set1, set2]) == [set2, set1]
