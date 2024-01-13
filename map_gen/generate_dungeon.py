"""Generator of dungeon type maps."""
from __future__ import annotations
from typing import List, TYPE_CHECKING
import random
from map_gen.ellipsis_room import EllipsisRoom

from map_gen.procgen import (
    place_entities,
    tunnel_between,
)
from map_gen.rectangular_room import RectangularRoom


from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from base_room import Room


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

    rooms: List[Room] = []

    for _r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        if random.random() > 0.8:
            # Theres a chance of the room being an ellipsis, use only with to keep them as circles.
            new_room = EllipsisRoom(x, y, room_width, room_width)
        else:
            new_room = RectangularRoom(x, y, room_width, room_height)

        # Run through the other rooms and see if they intersect with this one.
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue  # This room intersects, so go to the next attempt.
        # If there are no intersections then the room is valid.

        # Dig out this rooms inner area.
        for x, y in new_room.get_inner_points():
            dungeon.tiles[x, y] = tile_types.floor

        if len(rooms) == 0:
            # The first room, where the player starts.
            player.place(*new_room.center, dungeon)
        else:  # All rooms after the first.
            # Dig out a tunnel between this room and the previous one.
            has_placed_first_door = False
            has_placed_second_door = False
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                tile = dungeon.tiles[x, y]

                # From the start of the tunnel, the first non walkable tile is the wall we want
                # to place the door on. But we have to check if there already
                # are empty spaces around it.
                inner_area = rooms[-1].inner
                is_within_x_bounds = inner_area[0].start < x < inner_area[0].stop
                is_within_y_bounds = inner_area[1].start < y < inner_area[1].stop

                is_within_bounds = is_within_x_bounds and is_within_y_bounds
                walkable_count = len(list(dungeon.get_walkable_adjacent_tiles(x, y)))

                if not is_within_bounds and not has_placed_first_door:
                    # check if the tile is surrounded by no more than 3 walking tiles
                    if walkable_count <= 4:
                        dungeon.tiles[x, y] = tile_types.closed_door
                        has_placed_first_door = True
                        continue

                # when reaching the boundaries of the new_room add a door
                if (new_room.is_within_bounds(x, y)) and not has_placed_second_door:
                    if walkable_count <= 4:
                        dungeon.tiles[x, y] = tile_types.closed_door
                        has_placed_second_door = True
                        continue

                if tile == tile_types.closed_door and not walkable_count <= 5:
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
