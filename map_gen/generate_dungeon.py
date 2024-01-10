"""Generator of dungeon type maps."""
from __future__ import annotations
from typing import List, TYPE_CHECKING
import random

from map_gen.procgen import (
    place_entities,
    tunnel_between,
)
from map_gen.rectangular_room import RectangularRoom


from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine


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
    dungeon = GameMap(engine, map_width, map_height, entities=[player], name="Crypt")

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
            has_placed_door = False
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                tile = dungeon.tiles[x, y]

                if not tile["walkable"] and not has_placed_door:
                    dungeon.tiles[x, y] = tile_types.closed_door
                    has_placed_door = True
                    continue

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
