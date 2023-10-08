from .base import BaseModel


# def get_bounding_rect(rects: Iterator[Rect]) -> Rect:
#     points = it.chain.from_iterable([rect.vertices for rect in rects])
#     xs, ys = zip(*points)

#     left = min(xs)
#     right = max(xs)
#     top = max(ys)
#     bottom = min(ys)
#     width = abs(right - left)
#     height = abs(top - bottom)

#     return Rect(
#         x=left + (width / 2),
#         y=bottom + (height / 2),
#         width=width,
#         height=height,
#     )


class VectorMixin:
    def __neg__(self):
        return self.__class__(**{k: -v for k, v in self.dict().items()})

    def __truediv__(self, other):
        return self.__class__(**{k: v / other for k, v in self.dict().items()})

    def copy(self):
        return self.__class__(**self.dict())

    def as_tuple(self):
        return tuple(self.dict().values())

    def __getitem__(self, key):
        return self.as_tuple()[key]


class Vector2(BaseModel, VectorMixin):
    x: float = 0
    y: float = 0

    def __getitem__(self, key):
        return self.as_tuple()[key]
        

class Vector4(BaseModel, VectorMixin):
    w: float = 0
    x: float = 0
    y: float = 0
    z: float = 0

    @property
    def cumulative_width(self):
        return self.x + self.z

    @property
    def cumulative_height(self):
        return self.w + self.y

    def __add__(self, other):
        return Vector4(
            w = self.w + other.w,
            x = self.x + other.x,
            y = self.y + other.y,
            z = self.z + other.z,
        )

    def __iadd__(self, other):
        self.w += other.w
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self


class TopLeftPositionHelperMixin:
    """
    x and y are topleft coords
    """

    @property
    def center(self) -> Vector2:
        return Vector2(
            x=self.x + self.width / 2,
            y=self.y + self.height / 2,
        )

    @property
    def size(self) -> Vector2:
        return Vector2(self.width, self.height)

    @size.setter
    def size(self, new_size: Vector2) -> None:
        self.width = new_size.x
        self.height = new_size.y

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def center_left(self) -> Vector2:
        return Vector2(x=self.left, y=self.center.y)

    @property
    def center_right(self) -> Vector2:
        return Vector2(x=self.right, y=self.center.y)

    @property
    def bottom_center(self) -> Vector2:
        return Vector2(x=self.center.x, y=self.bottom)

    @property
    def top_center(self) -> Vector2:
        return Vector2(x=self.center.x, y=self.top)

    @property
    def top_left(self) -> Vector2:
        return Vector2(x=self.left, y=self.top)

    @top_left.setter
    def top_left(self, top_left: Vector2) -> None:
        self.x = top_left.x
        self.y = top_left.y

    @property
    def top_right(self) -> Vector2:
        return Vector2(x=self.right, y=self.top)

    @property
    def bottom_left(self) -> Vector2:
        return Vector2(x=self.left, y=self.bottom)

    @property
    def bottom_right(self) -> Vector2:
        return Vector2(x=self.right, y=self.bottom)


class Rect(TopLeftPositionHelperMixin):
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def copy(self):
        return Rect(
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height,
        )

    def expand_by_size(self, size: Vector4) -> "Rect":
        return Rect(
            x=self.x - size.z,
            y=self.y - size.w,
            width=self.width + size.cumulative_width,
            height=self.height + size.cumulative_height,
        )

    def __repr__(self):
        return (
            f"<Rect (x={self.x} y={self.y} "
            f"width={self.width} height={self.height})>"
        )
