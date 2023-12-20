from __future__ import annotations
from typing import Tuple

from map_gen.base_room import Room


class RectangularRoom(Room):
    """A rectangular room on the map."""

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)
