from __future__ import annotations
import random
from typing import List, Tuple

from map_gen.base_room import Room


class CaveLikeRoom(Room):
    """A cave-like room on the map using cellular automata."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        fill_probability: float,
        generations: int,
    ):
        """
        Initializes the cave-like room with given dimensions and cellular automata parameters.

        Parameters:
            x (int): The x-coordinate of the top-left corner of the room.
            y (int): The y-coordinate of the top-left corner of the room.
            width (int): The width of the cave-like room.
            height (int): The height of the cave-like room.
            fill_probability (float): Probability of a cell being filled initially.
            generations (int): Number of generations to run the cellular automata.
        """
        self.x1 = x
        self.y1 = y
        self.width = width
        self.height = height
        self.fill_probability = fill_probability
        self.generations = generations
        self.grid = self._initialize_grid()
        self._generate()

    def _initialize_grid(self) -> List[List[int]]:
        return [
            [
                1 if random.random() < self.fill_probability else 0
                for _ in range(self.width)
            ]
            for _ in range(self.height)
        ]

    def _count_filled_neighbors(self, grid: List[List[int]], x: int, y: int) -> int:
        count = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = x + dx, y + dy
                if (
                    (dx != 0 or dy != 0)
                    and 0 <= nx < self.width
                    and 0 <= ny < self.height
                ):
                    count += grid[ny][nx]
        return count

    def _generate(self):
        for _ in range(self.generations):
            new_grid = [
                [self.grid[y][x] for x in range(self.width)] for y in range(self.height)
            ]
            for y in range(self.height):
                for x in range(self.width):
                    filled_neighbors = self._count_filled_neighbors(self.grid, x, y)
                    if self.grid[y][x] == 1:
                        if filled_neighbors < 3:
                            new_grid[y][x] = 0  # Die if too lonely
                        elif filled_neighbors > 4:
                            new_grid[y][x] = 1  # Stay filled if enough neighbors
                    else:
                        if filled_neighbors > 5:
                            new_grid[y][x] = 1  # Become filled if surrounded
            self.grid = new_grid

    @property
    def size(self) -> int:
        """Return the size of this cave-like room, which is the count of filled tiles."""
        filled_tiles = sum(tile == 1 for row in self.grid for tile in row)
        return filled_tiles

    @property
    def inner(self) -> List[List[int]]:
        """Return the inner area of this cave-like room as a 2D grid."""
        return self.grid

    @property
    def center(self) -> Tuple[int, int]:
        """Return the center coordinates of this cave-like room."""
        return (self.x1 + self.width // 2, self.y1 + self.height // 2)

    def intersects(self, other: CaveLikeRoom) -> bool:
        """Return True if this room overlaps with another RectangularRoom."""
        return (
            self.x1 <= other.x1
            and self.x1 + self.width >= other.x1 + other.width
            and self.y1 <= other.y1
            and self.y1 + self.height >= other.y1 + other.height
        )
