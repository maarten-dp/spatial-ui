from dataclasses import dataclass

@dataclass(eq=True, unsafe_hash=True, frozen=True)
class Point:
    __slots__ = ("x", "y")



