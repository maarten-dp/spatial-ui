class QuantifiedValue:
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit

    def __eq__(self, other):
        same_value = self.value == other.value
        same_unit = self.unit == other.unit
        return same_value and same_unit
