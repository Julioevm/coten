from __future__ import annotations
from typing import Iterator, Tuple


class Room:
    """A generic room on the map."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def size(self) -> int:
        raise NotImplementedError("size function needs to be implemented.")

    def is_within_inner_bounds(self, x: int, y: int) -> bool:
        """Return True if the x and y coordinates are inside this room."""
        raise NotImplementedError(
            "is_within_inner_bounds function needs to be implemented."
        )

    def get_inner_points(self) -> Iterator[Tuple[int, int]]:
        """Yield points (x, y) that are inside the room."""
        raise NotImplementedError("get_inner_points function needs to be implemented.")

    def intersects(self, other: Room) -> bool:
        """Return True if this room overlaps with another Rectangular Room."""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )
