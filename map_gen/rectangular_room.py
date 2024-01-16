from __future__ import annotations
from typing import Iterator, Tuple

from map_gen.base_room import Room


class RectangularRoom(Room):
    """A rectangular room on the map."""

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def is_within_inner_bounds(self, x: int, y: int) -> bool:
        """Return True if the x and y coordinates are inside this room."""
        return self.x1 < x < self.x2 and self.y1 < y < self.y2

    def get_inner_points(self) -> Iterator[Tuple[int, int]]:
        """Yield points (x, y) that are inside the room."""
        for x in range(self.x1 + 1, self.x2):
            for y in range(self.y1 + 1, self.y2):
                yield (x, y)
