"""Utilities for procedural generation of maps."""

from __future__ import annotations
from typing import Dict, Iterator, List, Set, Tuple, TYPE_CHECKING
import random
import numpy as np
import tcod
from map_gen.rectangular_room import RectRoom
import tile_types

from map_gen import parameters, theme_factories
from utils import flip_coin, generate_rnd


if TYPE_CHECKING:
    from entity import Entity
    from game_map import GameMap
    from map_gen.base_room import Room
    from map_gen.encounter import Encounter


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


def get_encounter_for_level(
    floor: int,
) -> Encounter:
    """Get an encounter for a given floor."""
    entity_weighted_chances = {}

    for key, values in parameters.floor_encounters.items():
        if key > floor:
            break

        for value in values:
            entity = value[0]
            weighted_chance = value[1]

            entity_weighted_chances[entity] = weighted_chance

    encounters = list(entity_weighted_chances.keys())
    entity_weighted_chance_values = list(entity_weighted_chances.values())

    chose_encounter = random.choices(encounters, weights=entity_weighted_chance_values)[
        0
    ]

    return chose_encounter


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


def get_fixed_items(floor: int) -> List[Entity]:
    items_with_counts = parameters.fixed_item_by_floor.get(floor, [])
    result = [item for item, count in items_with_counts for _ in range(count)]
    return result


def place_room_entities(room: Room, dungeon: GameMap, floor: int):
    """
    Place entities in a given room a GameMap.
    """
    max_monsters = get_max_value_for_floor(parameters.max_room_monsters_by_floor, floor)
    max_items = get_max_value_for_floor(parameters.max_room_items_by_floor, floor)

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
                entity.spawn(x, y, dungeon)
                placed = True


def place_level_entities(dungeon: GameMap, floor: int):
    """
    Place entities in a given room a GameMap.
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
            x = generate_rnd(dungeon.width)
            y = generate_rnd(dungeon.height)

            if dungeon.tiles[x, y]["walkable"] and not any(
                e.x == x and e.y == y for e in dungeon.entities
            ):
                entity.spawn(x, y, dungeon)
                placed = True


def place_encounter(room: Room, dungeon: GameMap, floor: int) -> bool:
    """
    Place an encounter in a given room of a cave. Return true if the room is suitable.
    """

    encounter = get_encounter_for_level(floor)

    if not encounter.is_room_suitable(room):
        return False

    encounter_entities = encounter.enemies + encounter.items + encounter.decorations

    for entity in encounter_entities:
        placed = False
        while not placed:
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)

            if dungeon.tiles[x, y]["walkable"] and not any(
                e.x == x and e.y == y for e in dungeon.entities
            ):
                entity.spawn(x, y, dungeon)
                placed = True

    return True


def is_near_theme_room(origin: Tuple[int, int], map: GameMap, offset: int = 5):
    for theme_room in map.theme_rooms:
        # Calculate the extended boundaries of the room
        left_boundary = max(theme_room.x - offset, 0)
        right_boundary = min(theme_room.x + theme_room.width + offset, map.width)
        top_boundary = max(theme_room.y - offset, 0)
        bottom_boundary = min(theme_room.y + theme_room.height + offset, map.height)

        # Check if the origin is within the extended boundaries
        if (
            left_boundary <= origin[0] <= right_boundary
            and top_boundary <= origin[1] <= bottom_boundary
        ):
            return True

    return False


def flood_fill(
    start: Tuple[int, int],
    dungeon: np.ndarray,
    floor: int,
    visited: Set[Tuple[int, int]],
    map: GameMap,
) -> Set[Tuple[int, int]]:
    stack = [start]
    while stack:
        x, y = stack.pop()
        if (
            (x, y) not in visited
            and dungeon[x][y] == floor
            and 0 <= x < map.width
            and 0 <= y < map.height
        ):
            visited.add((x, y))
            # Add the neighboring tiles to the stack if they're within bounds
            neighbors = [
                (x - 1, y),
                (x + 1, y),
                (x, y - 1),
                (x, y + 1),
                (x - 1, y - 1),
                (x - 1, y + 1),
                (x + 1, y - 1),
                (x + 1, y + 1),
            ]
            for nx, ny in neighbors:
                stack.append((nx, ny))

    return visited


def get_size_for_theme_room(
    floor, origin, min_size, max_size, map: GameMap, dungeon: np.ndarray
) -> Tuple[int, int] | None:
    DMAXX = map.width
    DMAXY = map.height
    if origin[0] + max_size > DMAXX and origin[1] + max_size > DMAXY:
        return None
    if is_near_theme_room(origin, map, max_size):
        return None

    max_width = min(max_size, DMAXX - origin[0])
    max_height = min(max_size, DMAXY - origin[1])

    room = (max_width, max_height)

    for i in range(max_size):
        width = i if i < room[1] else 0
        if i < max_height:
            while width < room[0]:
                if dungeon[origin[0] + width][origin[1] + i] != floor:
                    break
                width += 1

        height = i if i < room[0] else 0
        if i < max_width:
            while height < room[1]:
                if dungeon[origin[0] + i][origin[1] + height] != floor:
                    break
                height += 1

        if width < min_size or height < min_size:
            if i < min_size:
                return None
            break

        room = (min(room[0], width), min(room[1], height))

    return (room[0], room[1])


def find_theme_rooms(
    min_size: int,
    max_size: int,
    floor: int,
    map: GameMap,
    dungeon: np.ndarray,
    rnd_size: bool = False,
    freq: int = 0,
):
    DMAXX = map.width
    DMAXY = map.height

    roll = flip_coin(freq) if freq > 0 else True

    for j in range(DMAXY - 1):
        for i in range(DMAXX - 1):
            if dungeon[i][j] == floor and roll:
                theme_size = get_size_for_theme_room(
                    floor, [i, j], min_size, max_size, map, dungeon
                )
                if theme_size is None:
                    continue

                if rnd_size:
                    min_dim = min_size - 2
                    max_dim = max_size - 2
                    rand_theme_x = min_dim + generate_rnd(
                        generate_rnd(theme_size[0] - min_dim + 1)
                    )
                    if rand_theme_x < min_dim or rand_theme_x > max_dim:
                        rand_theme_x = min_dim
                    new_theme_y = min_dim + generate_rnd(
                        generate_rnd(theme_size[1] - min_dim + 1)
                    )
                    if new_theme_y < min_dim or new_theme_y > max_dim:
                        new_theme_y = min_dim

                map.theme_rooms.add(RectRoom(i, j, theme_size[0], theme_size[1]))


def paint_theme_rooms(map: GameMap):
    """
    Debug function that paints theme rooms on the game map with red and blue tiles.
    """

    for room in map.theme_rooms:
        for i in range(room.x, room.x + room.width):
            for j in range(room.y, room.y + room.height):
                i = min(i, map.width - 1)
                j = min(j, map.height - 1)
                if map.tiles[i][j] == tile_types.floor:
                    map.tiles[i][j] = tile_types.red
                else:
                    map.tiles[i][j] = tile_types.blue


def check_enclosed_room(room: RectRoom, map: GameMap):
    """Checks if a room is enclosed by non floor walls"""

    # Check top and bottom rows of the area
    for i in range(room.x, room.x + room.width):
        if (
            map.tiles[i][room.y - 1] == tile_types.floor
            or map.tiles[i][room.y + room.height] == tile_types.floor
        ):
            return False

    # Check left and right columns of the area
    for i in range(room.y, room.y + room.height):
        if (
            map.tiles[room.x - 1][i] == tile_types.floor
            or map.tiles[room.x + room.width][i] == tile_types.floor
        ):
            return False

    return True


def create_theme_rooms(map: GameMap):
    theme_rooms_stack = [theme_factories.shrine]

    while theme_rooms_stack:
        theme_room = theme_rooms_stack.pop(generate_rnd(len(theme_rooms_stack)))

        for room in map.theme_rooms:

            if theme_room.enclosed and not check_enclosed_room(room, map):
                continue

            items = theme_room.encounter.items
            decorations = theme_room.encounter.decorations
            enemies = theme_room.encounter.enemies

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
