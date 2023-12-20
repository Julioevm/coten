from __future__ import annotations
from typing import Tuple


class RectangularRoom:
    """A rectangular room on the map."""

    def __init__(self, x: int, y: int, width: int, height: int):
        """
        Initializes the object with the given coordinates and dimensions.

        Parameters:
            x (int): The x-coordinate of the top-left corner of the object.
            y (int): The y-coordinate of the top-left corner of the object.
            width (int): The width of the object.
            height (int): The height of the object.
        """
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
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        """Return True if this room overlaps with another RectangularRoom."""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )
