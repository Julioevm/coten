from __future__ import annotations
import itertools

import random
from typing import Iterable, Iterator, List, Optional, TYPE_CHECKING, Tuple

import numpy as np
import tcod  # type: ignore
from tcod.console import Console
from components.consumable import HealingConsumable
from map_gen.rectangular_room import RectRoom

import tile_types
from entity import Actor, Item

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:
    """Class to manage map mechanics, and render the map to the console."""

    def __init__(
        self,
        engine: Engine,
        width: int,
        height: int,
        entities: Iterable[Entity] = (),
        fill_wall_tile=tile_types.wall,
        name="???",
    ):
        """
        Initializes a new instance of the class.
        """
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.fill_wall_tile = fill_wall_tile
        self.tiles = np.full((width, height), fill_value=fill_wall_tile, order="F")
        self.theme_rooms = set[RectRoom]()
        self.bloody_tiles = set()
        self.name = name

        self.visible = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player can currently see
        self.explored = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player has seen before

        self.upstairs_location: tuple[int, int] = (0, 0)
        self.downstairs_location: tuple[int, int] = (0, 0)

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    @property
    def healing_items(self) -> Iterator[Item]:
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Item)
            and entity.consumable
            and isinstance(entity.consumable, HealingConsumable)
        )

    def get_blocking_entity_at_location(
        self,
        location_x: int,
        location_y: int,
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity is not None
                and entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity

        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def is_in_fov(self, x: int, y: int):
        return self.visible[x, y]

    def get_actors_in_fov(self):
        actors = set([])
        for actor in self.actors:
            if self.is_in_fov(actor.x, actor.y):
                actors.add(actor)
        return actors

    def get_closest_actor(self, x: int, y: int) -> Optional[Actor]:
        closest_distance = 100
        closest_actor = None
        for actor in self.get_actors_in_fov() - {self.engine.player}:
            if actor.x == x and actor.y == y:
                return actor
            dx = actor.x - x
            dy = actor.y - y
            distance = distance = max(abs(dx), abs(dy))
            if distance < closest_distance:
                closest_distance = distance
                closest_actor = actor
        return closest_actor

    def get_item_at_location(self, x: int, y: int) -> Optional[Item]:
        return next((item for item in self.items if item.x == x and item.y == y), None)

    def get_random_empty_tile(
        self, x: int, y: int, width: int, height: int
    ) -> Optional[tuple[int, int]]:
        for _ in range(100):
            x = min(np.random.randint(x, x + width - 1), self.width - 1)
            y = min(np.random.randint(y, y + height - 1), self.height - 1)
            if (
                self.tiles[x, y]["walkable"]
                and not self.get_blocking_entity_at_location(x, y)
                and not self.get_actor_at_location(x, y)
                and not self.get_item_at_location(x, y)
            ):
                return x, y

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_walkable_tiles_from_position(
        self, origin: Tuple[int, int], game_map: GameMap
    ) -> List[Tuple[int, int]]:
        """Perform a flood-fill to find which areas the current position has access to."""
        walkable_tiles = []
        stack = [(origin[0], origin[1])]
        while stack:
            x, y = stack.pop()
            if (x, y) not in walkable_tiles and game_map.tiles["walkable"][x, y]:
                walkable_tiles.append((x, y))
                stack.extend(
                    [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
                )
        return walkable_tiles

    def get_walkable_adjacent_tiles(self, x: int, y: int) -> Iterator[tuple[int, int]]:
        """Get all walkable adjacent tiles to the given (x, y) coordinate."""
        for x_offset, y_offset in itertools.product((-1, 0, 1), (-1, 0, 1)):
            if x_offset == 0 and y_offset == 0:
                continue
            if not self.in_bounds(x + x_offset, y + y_offset):
                continue
            if not self.tiles[x + x_offset, y + y_offset]["walkable"]:
                continue
            yield x + x_offset, y + y_offset

    def has_adjacent_door_tiles(self, x: int, y: int) -> bool:
        for x_offset, y_offset in itertools.product((-1, 0, 1), (-1, 0, 1)):
            if x_offset == 0 and y_offset == 0:
                continue
            if not self.in_bounds(x + x_offset, y + y_offset):
                continue
            if not self.tiles[x + x_offset, y + y_offset] == tile_types.closed_door:
                continue
            return True
        return False

    def _find_suitable_walls(self, room: RectRoom):
        """Find a suitable wall to place a door on.
        A suitable wall is a wall that is surrounded by floor tiles on both sides.
        And most not have a door already placed on it."""
        suitable_walls = []

        skip_top = False
        skip_bottom = False
        skip_left = False
        skip_right = False

        # Check top and bottom walls
        for x in range(room.x, room.x + room.width):
            if self.tiles[x, room.y] == tile_types.closed_door:
                skip_top = True

        if not skip_top:
            top_wall = [
                (x, room.y)
                for x in range(room.x, room.x + room.width)
                if self.tiles[x, room.y] == tile_types.wall
                and self.tiles[x, room.y - 1] == tile_types.floor
                and self.tiles[x, room.y + 1] == tile_types.floor
            ]

            suitable_walls.extend(top_wall)

        for x in range(room.x, room.x + room.width):
            if self.tiles[x, room.y + room.height] == tile_types.closed_door:
                skip_bottom = True

        if not skip_bottom:
            bottom_wall = [
                (x, room.y + room.height)
                for x in range(room.x, room.x + room.width)
                if self.tiles[x, room.y + room.height] == tile_types.wall
                and self.tiles[x, min(room.y + room.height + 1, self.height - 1)]
                == tile_types.floor
                and self.tiles[x, max(room.y + room.height - 1, 0)] == tile_types.floor
            ]

            suitable_walls.extend(bottom_wall)

        # Check left and right walls

        for y in range(room.y, room.y + room.height):
            if self.tiles[room.x, y] == tile_types.closed_door:
                skip_left = True

        if not skip_left:
            left_wall = [
                (room.x, y)
                for y in range(room.y, room.y + room.height)
                if self.tiles[room.x, y] == tile_types.wall
                and self.tiles[room.x - 1, y] == tile_types.floor
                and self.tiles[room.x + 1, y] == tile_types.floor
            ]

            suitable_walls.extend(left_wall)

        for y in range(room.y, room.y + room.height):
            if self.tiles[room.x + room.width, y] == tile_types.closed_door:
                skip_right = True

        if not skip_right:
            right_wall = [
                (room.x + room.width, y)
                for y in range(room.y, room.y + room.height)
                if self.tiles[room.x + room.width, y] == tile_types.wall
                and self.tiles[min(room.x + room.width + 1, self.width - 1), y]
                == tile_types.floor
                and self.tiles[room.x + room.width - 1, y] == tile_types.floor
            ]

            suitable_walls.extend(right_wall)

        return suitable_walls

    def place_door(self, room: RectRoom):
        """Place a door on a random suitable wall of the room."""
        suitable_walls = self._find_suitable_walls(room)
        if suitable_walls:
            chosen_wall = random.choice(suitable_walls)
            self.tiles[chosen_wall] = tile_types.closed_door

    def render_basic(self, console: Console) -> None:
        console.rgb[0 : self.width, 0 : self.height] = self.tiles["light"]

    def render_with_light(self, console: Console) -> None:
        """Render the map with the light effect. Entities with the has_light will generate light."""
        dim_adjustment = 0.4  # Increase this value to decrease the dimming effect

        lights = [entity for entity in self.entities if entity.has_light]

        # Calculate the distance from each light object to each tile on the map
        distances = np.zeros((self.width, self.height, len(lights)))
        for i, light in enumerate(lights):
            distances[:, :, i] = np.sqrt(
                (np.arange(self.width)[:, None] - light.x) ** 2
                + (np.arange(self.height) - light.y) ** 2
            )

        # Calculate the dim factor for each tile based on the distance to the closest light object
        dim_factor = np.min(distances, axis=2)
        dim_factor = self.calculate_dim_factor(dim_factor, dim_adjustment)

        # Apply the dimming effect to the light colors
        light_colors = self.tiles["light"]
        dimmed_light_colors = np.empty_like(light_colors)
        dimmed_light_colors["ch"] = light_colors["ch"]
        for color in ["fg", "bg"]:
            dim_factor_reshaped = dim_factor.reshape(self.width, self.height, 1)
            dimmed_light_colors[color] = (
                light_colors[color].astype(np.float32) * dim_factor_reshaped
            ).astype(np.uint8)

        # Render the dimmed tiles
        console.rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[dimmed_light_colors, self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        # Modify the background color of bloody tiles
        for x, y in self.bloody_tiles:
            if self.in_bounds(x, y) and self.visible[x, y]:
                bloodify_tile(x, y, console)

        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            # Calculate the distance from the entity to the closest light object
            distances = np.sqrt(
                list(
                    (entity.x - light.x) ** 2 + (entity.y - light.y) ** 2
                    for light in lights
                )
            )
            distance = np.min(distances)

            entity_dim_factor = self.calculate_dim_factor(distance, dim_adjustment)

            # Apply the dim factor to the entity's color
            dimmed_color = tuple(
                (np.array(entity.color, dtype=np.float32) * entity_dim_factor).astype(
                    np.uint8
                )
            )

            # Only print entities that are in the FOV
            if self.visible[entity.x, entity.y]:
                console.print(entity.x, entity.y, entity.char, fg=dimmed_color)

    def calculate_dim_factor(
        self, distance: float | np.ndarray, adjustment: float
    ) -> np.ndarray:
        dim_factor = 1 / (distance + 1) + adjustment
        return np.clip(dim_factor, 0, 1)

    def reveal_map(self) -> None:
        """Reveals the entire map."""
        self.explored = np.full((self.width, self.height), fill_value=True, order="F")

    def is_line_of_sight_clear(
        self, start_x: int, start_y: int, end_x: int, end_y: int
    ) -> bool:
        """Check if a straight line path is clear of obstacles."""
        tiles = self.tiles  # Assumes you have a tiles structure similar to get_path_to
        walkable = tiles["walkable"]

        # Bresenham's Line Algorithm
        points = tcod.los.bresenham(start=(start_x, start_y), end=(end_x, end_y))
        for x, y in points:
            # If the tile is not walkable, there is an obstacle in the way.
            if not walkable[x, y]:
                return False
        return True

    def render(self, console: Console) -> None:
        if self.engine.player is None:
            self.render_basic(console)
        else:
            self.render_with_light(console)


def bloodify_tile(x: int, y: int, console: Console) -> None:
    """Changes the tile at the given (x, y) coordinate to blood."""
    # Retrieve the current tile values at position (x, y)
    char, fg, bg = console.rgb[x, y]

    # Blend the existing bg color with red
    red_bg = (min(bg[0] * 1.5, 255), bg[1] * 0.7, bg[2] * 0.7)

    # Set the new background color, keeping the char and fg color the same
    console.rgb[x, y] = (char, fg, red_bg)
