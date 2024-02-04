"""Generator of dungeon type maps."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, List

from map_gen import parameters

import tile_types
from game_map import GameMap
from map_gen.ellipsis_room import EllipsisRoom
from map_gen.procgen import (
    get_max_value_for_floor,
    place_encounter,
    place_entities,
    tunnel_between,
)
from map_gen.rectangular_room import RectangularRoom

if TYPE_CHECKING:
    from base_room import Room

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
    DUNGEON_ENCOUNTER_CHANCE = 0.1
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player], name="Crypt")
    floor = engine.game_world.current_floor
    max_encounters = get_max_value_for_floor(parameters.max_encounters_by_floor, floor)
    current_encounters = 0

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
            if player is not None:
                player.place(*new_room.center, dungeon)
        else:  # All rooms after the first.
            # Dig out a tunnel between this room and the previous one.
            has_placed_first_door = False
            has_placed_second_door = False

            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                tile = dungeon.tiles[x, y]
                is_within_bounds = rooms[-1].is_within_inner_bounds(x, y)
                walkable_count = len(list(dungeon.get_walkable_adjacent_tiles(x, y)))

                if not is_within_bounds and not has_placed_first_door:
                    # check if the tile is surrounded by no more than 4 walking tiles
                    if walkable_count <= 4:
                        dungeon.tiles[x, y] = tile_types.closed_door
                        has_placed_first_door = True
                        continue

                # when reaching the boundaries of the new_room add a door
                if (
                    new_room.is_within_inner_bounds(x, y)
                ) and not has_placed_second_door:
                    if walkable_count <= 4:
                        dungeon.tiles[x, y] = tile_types.closed_door
                        has_placed_second_door = True
                        continue

                if tile == tile_types.closed_door and not walkable_count <= 5:
                    continue
                dungeon.tiles[x, y] = tile_types.floor
        if player is not None:
            if (
                current_encounters <= max_encounters
                and len(rooms) > 0  # Skip first room
                and random.random() < DUNGEON_ENCOUNTER_CHANCE
            ):
                if place_encounter(new_room, dungeon, floor):
                    current_encounters += 1
                else:
                    place_entities(new_room, dungeon, floor)
            else:
                place_entities(new_room, dungeon, floor)

        rooms.append(new_room)

    # Place stairs going down to the previous level, unless this is the first level.

    if floor > 1:
        dungeon.tiles[rooms[0].center] = tile_types.down_stairs
        dungeon.downstairs_location = rooms[0].center

    dungeon.tiles[rooms[-1].center] = tile_types.up_stairs
    dungeon.upstairs_location = rooms[-1].center

    return dungeon
