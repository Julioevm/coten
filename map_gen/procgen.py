"""Utilities for procedural generation of maps."""
from __future__ import annotations
from typing import Dict, Iterator, List, Tuple, TYPE_CHECKING
import random
import tcod

from map_gen import parameters


if TYPE_CHECKING:
    from entity import Entity
    from game_map import GameMap
    from map_gen.base_room import Room


def get_max_value_for_floor(
    max_value_by_floor: List[Tuple[int, int]], floor: int
) -> int:
    """Iterate though the list and find the max value for the given floor."""
    current_value = 0

    for floor_minimum, value in max_value_by_floor:
        if floor_minimum > floor:
            break

        current_value = value

    return current_value


def get_entities_at_random(
    weighted_chances_by_floor: Dict[int, List[Tuple[Entity, int]]],
    number_of_entities: int,
    floor: int,
) -> List[Entity]:
    """Get a list of entities from a list based on their weight, with a given number for a specific floor."""
    entity_weighted_chances = {}

    for key, values in weighted_chances_by_floor.items():
        if key > floor:
            break

        for value in values:
            entity = value[0]
            weighted_chance = value[1]

            entity_weighted_chances[entity] = weighted_chance

    entities = list(entity_weighted_chances.keys())
    entity_weighted_chance_values = list(entity_weighted_chances.values())

    chosen_entities = random.choices(
        entities, weights=entity_weighted_chance_values, k=number_of_entities
    )

    return chosen_entities


def tunnel_between(
    start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points."""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5:  # 50% chance.
        # Move horizontally, then vertically.
        corner_x, corner_y = x2, y1
    else:
        # Move vertically, then horizontally.
        corner_x, corner_y = x1, y2

    # Generate the coordinates for this tunnel.
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y


def place_entities(room: Room, dungeon: GameMap, floor: int):
    """
    Place entities in a given room of a cave.
    """
    max_monsters = get_max_value_for_floor(parameters.max_monsters_by_floor, floor)
    max_items = get_max_value_for_floor(parameters.max_items_by_floor, floor)

    num_monsters = random.randint(0, max_monsters)
    num_items = random.randint(0, max_items)

    monsters = get_entities_at_random(parameters.enemy_chances, num_monsters, floor)
    items = get_entities_at_random(parameters.item_chances, num_items, floor)

    for entity in monsters + items:
        placed = False
        while not placed:
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)

            if dungeon.tiles[x, y]["walkable"] and not any(
                e.x == x and e.y == y for e in dungeon.entities
            ):
                entity.spawn(dungeon, x, y)
                placed = True
