from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np  # type: ignore
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

        self.upstairs_location = (0, 0)
        self.downstairs_location = (0, 0)

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

    def get_item_at_location(self, x: int, y: int) -> Optional[Item]:
        return next((item for item in self.items if item.x == x and item.y == y), None)

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        console.rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
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
            # Only print entities that are in the FOV
            if self.visible[entity.x, entity.y]:
                console.print(
                    x=entity.x, y=entity.y, string=entity.char, fg=entity.color
                )

    def reveal_map(self) -> None:
        """Reveals the entire map."""
        self.explored = np.full((self.width, self.height), fill_value=True, order="F")


def bloodify_tile(x: int, y: int, console: Console) -> None:
    """Changes the tile at the given (x, y) coordinate to blood."""
    # Retrieve the current tile values at position (x, y)
    char, fg, bg = console.rgb[x, y]

    # Blend the existing bg color with red
    red_bg = (min(bg[0] * 1.5, 255), bg[1] * 0.7, bg[2] * 0.7)

    # Set the new background color, keeping the char and fg color the same
    console.rgb[x, y] = (char, fg, red_bg)
