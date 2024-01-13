from __future__ import annotations
from typing import Iterator, Tuple

from map_gen.base_room import Room


class EllipsisRoom(Room):
    """An ellipsis-shaped room on the map."""

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        # This is an approximation using the bounding box of the ellipse.
        # This will be rectangular so don't use it to check the actual room.
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def is_within_bounds(self, x: int, y: int) -> bool:
        """Return True if the x and y coordinates are inside this room."""
        # Center of the ellipse
        h = (self.x2 + self.x1) / 2
        k = (self.y2 + self.y1) / 2
        # Radii of the ellipse
        a = (self.x2 - self.x1) / 2
        b = (self.y2 - self.y1) / 2
        # Check if the point (x, y) is within the ellipse
        return ((x - h) ** 2) / (a ** 2) + ((y - k) ** 2) / (b ** 2) <= 1

    def get_inner_points(self) -> Iterator[Tuple[int, int]]:
        """Yield points (x, y) that are inside the room."""
        for x in range(self.x1, self.x2 + 1):
            for y in range(self.y1, self.y2 + 1):
                if self.is_within_bounds(x, y):
                    yield (x, y)