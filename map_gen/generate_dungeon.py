"""Generator of dungeon type maps."""
from __future__ import annotations
from typing import List, TYPE_CHECKING
import random

from map_gen.procgen import (
    get_entities_at_random,
    get_max_value_for_floor,
    tunnel_between,
)
from map_gen.rectangular_room import RectangularRoom
import parameters


from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


def place_entities(room: RectangularRoom, dungeon: GameMap, floor_number: int) -> None:
    """
    Place entities in a given room of a dungeon.

    Args:
        room (RectangularRoom): The room in which entities will be placed.
        dungeon (GameMap): The dungeon map.
        maximum_monsters (int): The maximum number of monsters to place.

    Returns:
        None
    """
    number_of_monsters = random.randint(
        0, get_max_value_for_floor(parameters.max_monsters_by_floor, floor_number)
    )
    number_of_items = random.randint(
        0, get_max_value_for_floor(parameters.max_items_by_floor, floor_number)
    )

    monsters: List[Entity] = get_entities_at_random(
        parameters.enemy_chances, number_of_monsters, floor_number
    )
    items: List[Entity] = get_entities_at_random(
        parameters.item_chances, number_of_items, floor_number
    )

    for entity in monsters + items:
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            entity.spawn(dungeon, x, y)


def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    engine: Engine,
) -> GameMap:
    """Generate a new dungeon map."""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []

    for _r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        # "RectangularRoom" class makes rectangles easier to work with
        new_room = RectangularRoom(x, y, room_width, room_height)

        # Run through the other rooms and see if they intersect with this one.
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue  # This room intersects, so go to the next attempt.
        # If there are no intersections then the room is valid.

        # Dig out this rooms inner area.
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # The first room, where the player starts.
            player.place(*new_room.center, dungeon)
        else:  # All rooms after the first.
            # Dig out a tunnel between this room and the previous one.
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor

        place_entities(new_room, dungeon, engine.game_world.current_floor)

        rooms.append(new_room)

    # Place stairs going down to the previous level, unless this is the first level.

    if engine.game_world.current_floor > 1:
        dungeon.tiles[rooms[0].center] = tile_types.down_stairs
        dungeon.downstairs_location = rooms[0].center

    dungeon.tiles[rooms[-1].center] = tile_types.up_stairs
    dungeon.upstairs_location = rooms[-1].center

    return dungeon
