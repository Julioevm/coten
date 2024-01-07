from __future__ import annotations

from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor


def set_bloody_tiles(engine: Engine, target: Actor) -> None:
    """Set the bloody tiles position for targeted entities."""
    engine.game_map.bloody_tiles.add((target.x, target.y))
    # Small random chance of adding one adjacent tile to the bloody tile list
    if random.random() < 0.2:
        adjacent_tiles = [
            (target.x + 1, target.y),
            (target.x - 1, target.y),
            (target.x, target.y + 1),
            (target.x, target.y - 1),
        ]
        random_tile = random.choice(adjacent_tiles)
        engine.game_map.bloody_tiles.add(random_tile)
