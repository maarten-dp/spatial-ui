from ..parser.constant import DEFAULT_PROPERTY_VALUES


class StyleRules:
    def __init__(self):
        self.rule_sets = []

    def __getattr__(self, key):
        key = key.replace('_', '-')
        for rule in self.rule_sets:
            if key in rule.values:
                return rule.values[key]
        if key in DEFAULT_PROPERTY_VALUES:
            return DEFAULT_PROPERTY_VALUES[key]
        raise AttributeError(f"No attribute named {key}")

    def add_rule_set(self, rule_set):
        self.rule_sets.append(rule_set)
        self.sort()

    def add_rule_sets(self, rule_sets):
        self.rule_sets.extend(rule_sets)
        self.sort()

    def sort(self):
        self.rule_sets.sort(reverse=True)


class RuleSet:
    def __init__(self, canonical, selector, values=None):
        self.canonical = canonical
        self.selector = selector
        if values is None:
            values = {}
        self.values = values

    def __lt__(self, other):
        return self.selector.specificity() < other.selector.specificity()

    def __gt__(self, other):
        return self.selector.specificity() > other.selector.specificity()

    def __le__(self, other):
        return self.selector.specificity() <= other.selector.specificity()

    def __ge__(self, other):
        return self.selector.specificity() >= other.selector.specificity()        

    def add_value(self, name, value):
        self.values[name] = value

    def __repr__(self):
        return self.canonical
