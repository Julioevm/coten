from __future__ import annotations
import itertools

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np
import tcod  # type: ignore
from tcod.console import Console
from components.consumable import HealingConsumable

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
                entity.blocks_movement
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

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

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

    def render(self, console: Console) -> None:
        """
        Renders the map with dimming light effect based on distance from the player position.
        """

        dim_adjustment = 0.4  # Increase this value to decrease the dimming effect
        # Calculate the distance from the player position for each tile
        distance_from_player = np.sqrt(
            (np.arange(self.width)[:, None] - self.engine.player.x) ** 2
            + (np.arange(self.height) - self.engine.player.y) ** 2
        )

        # Apply dimming effect based on the distance from the player position
        dim_factor = self.calculate_dim_factor(distance_from_player, dim_adjustment)

        # Apply the dimming factor to the light colors
        light_colors = self.tiles["light"]
        dimmed_light_colors = np.empty_like(light_colors)
        dimmed_light_colors["ch"] = light_colors["ch"]
        for color in ["fg", "bg"]:
            # Reshape dim_factor to be broadcastable with the color arrays
            dim_factor_reshaped = dim_factor.reshape(self.width, self.height, 1)
            dimmed_light_colors[color] = (
                light_colors[color].astype(np.float32) * dim_factor_reshaped
            ).astype(
                np.uint8
            )  # Assuming colors are 8-bit

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
            # Calculate the distance from the entity to the player
            distance = entity.distance(self.engine.player.x, self.engine.player.y)

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

    def calculate_dim_factor(self, distance: float, adjustment: float) -> float:
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


def bloodify_tile(x: int, y: int, console: Console) -> None:
    """Changes the tile at the given (x, y) coordinate to blood."""
    # Retrieve the current tile values at position (x, y)
    char, fg, bg = console.rgb[x, y]

    # Blend the existing bg color with red
    red_bg = (min(bg[0] * 1.5, 255), bg[1] * 0.7, bg[2] * 0.7)

    # Set the new background color, keeping the char and fg color the same
    console.rgb[x, y] = (char, fg, red_bg)
