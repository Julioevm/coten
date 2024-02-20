from collections import namedtuple
import random
import numpy as np
from game_map import GameMap
from map_gen import encounter_factories
from map_gen.encounter import Encounter
from map_gen.rectangular_room import RectRoom

import entity_factories
import tile_types

Wall = namedtuple("Wall", ["is_vertical", "x", "y", "length"])


class ThemeRoom:
    def __init__(
        self,
        name: str,
        encounter: Encounter,
        enclosed: bool,
    ):
        self.name = name
        self.encounter = encounter
        self.enclosed = enclosed

    def place(self, room: RectRoom, map: GameMap) -> None:
        self._place_entities(room, map)
        self._set_decorations(room, map)

    def _place_entities(self, room: RectRoom, map: GameMap) -> None:
        "Place the encounter entities randomly in the room."
        items = self.encounter.items
        decorations = self.encounter.decorations
        enemies = self.encounter.enemies

        for item in items:
            position = map.get_random_empty_tile(
                room.x, room.y, room.width, room.height
            )
            if position:
                item.spawn(*position, map)

        for enemy in enemies:
            position = map.get_random_empty_tile(
                room.x, room.y, room.width, room.height
            )
            if position:
                enemy.spawn(*position, map)

        for decoration in decorations:
            position = map.get_random_empty_tile(
                room.x, room.y, room.width, room.height
            )
            if position:
                decoration.spawn(*position, map)

    def _set_decorations(self, room: RectRoom, map: GameMap) -> None:
        "Place the theme specific decorations in the room."
        pass


class ShrineRoom(ThemeRoom):
    def __init__(self):
        self.name = "Shrine"
        self.encounter = encounter_factories.shrine
        self.enclosed = True
        self.decorations = [
            entity_factories.torch,
            entity_factories.shrine,
            entity_factories.torch,
        ]
        self.layout = np.array(
            [
                [tile_types.wall, tile_types.wall, tile_types.wall],
                [tile_types.floor, tile_types.floor, tile_types.floor],
            ]
        )

    def _find_suitable_walls(self, room: RectRoom, map: GameMap) -> list[Wall]:
        suitable_walls = []
        found_top = True
        found_bottom = True
        found_left = True
        found_right = True

        # Check top and bottom walls
        for x in range(room.x1, room.x2):
            if map.tiles[x, room.y1 - 1] != tile_types.wall:
                found_top = False
            if map.tiles[x, room.y2 + 1] != tile_types.wall:
                found_bottom = False

        # Check left and right walls
        for y in range(room.y1, room.y2):
            if map.tiles[room.x1 - 1, y] != tile_types.wall:
                found_left = False
            if map.tiles[room.x2 + 1, y] != tile_types.wall:
                found_right = False

        if found_top:
            suitable_walls.append(Wall(False, room.x1, room.y1, room.width))
        if found_bottom:
            suitable_walls.append(Wall(False, room.x1, room.y2, room.width))
        if found_left:
            suitable_walls.append(Wall(True, room.x1, room.y2, room.height))
        if found_right:
            suitable_walls.append(Wall(True, room.x2, room.y2, room.height))
        return suitable_walls

    def _pick_wall(self, suitable_walls: list[Wall]) -> Wall:
        return random.choice(suitable_walls)

    def _place_decorations(self, wall: Wall, map: GameMap) -> None:
        if wall.is_vertical:
            x = wall.x
            y = wall.y + wall.length // 2
            for i, decoration in enumerate(self.decorations):
                decoration.spawn(x, y + i, map)
        else:
            x = wall.x + wall.length // 2
            y = wall.y
            for j, decoration in enumerate(self.decorations):
                decoration.spawn(x + j, y, map)

    def _set_decorations(self, room: RectRoom, map: GameMap) -> None:
        suitable_walls = self._find_suitable_walls(room, map)
        if suitable_walls:
            chosen_wall = self._pick_wall(suitable_walls)
            self._place_decorations(chosen_wall, map)
