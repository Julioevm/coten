"""Generator of cathedral type maps."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, List

from map_gen import parameters

import tile_types
from game_map import GameMap
from map_gen.procgen import (
    get_max_value_for_floor,
)
from map_gen.rectangular_room import RectangularRoom

if TYPE_CHECKING:
    from base_room import Room
    from engine import Engine

rooms: List[Room] = []
max_encounters = 0
current_encounters = 0


def flip_coin():
    return random.choice([True, False])


def generate_dungeon(
    map_width: int,
    map_height: int,
    engine: Engine,
) -> GameMap:
    global max_encounters
    player = engine.player
    dungeon = GameMap(
        engine, map_width, map_height, entities=[player], name="Cathedral"
    )
    floor = engine.game_world.current_floor
    max_encounters = get_max_value_for_floor(parameters.max_encounters_by_floor, floor)

    first_room(dungeon)

    return dungeon


def map_room(room: RectangularRoom, dungeon: GameMap):
    global rooms
    rooms.append(room)
    for x, y in room.get_inner_points():
        dungeon.tiles[x, y] = tile_types.floor


def check_room(room: RectangularRoom, dungeon: GameMap):
    print(f"Check room x{room.x1} y{room.y1} w{room.width} h{room.height}")
    global rooms
    if room.x2 > dungeon.width or room.y2 > dungeon.height:
        print("Room out of bounds")
        return False
    if any(room.intersects(other_room) for other_room in rooms):
        print("Room intersects another room")
        return False

    return True


def generate_room(area: RectangularRoom, dungeon: GameMap, verticalLayout: bool):
    print(f"Generate room x{area.x1} y{area.y1} w{area.width} h{area.height}")
    place_room1 = False

    for _ in range(20):
        x1 = area.x1
        y1 = area.y1
        random_width = (random.randint(0, 4) + 2) & ~1
        random_height = (random.randint(0, 4) + 2) & ~1

        if verticalLayout:
            x1 += -random_width
            y1 += int(area.height / 2 - random_height / 2)
            room1 = RectangularRoom(x1, y1, random_width, random_height)
            place_room1 = check_room(
                RectangularRoom(x1 - 1, y1 - 1, random_width + 1, random_height + 2),
                dungeon,
            )
        else:
            x1 += int(area.width / 2 - random_width / 2)
            y1 += -random_height
            room1 = RectangularRoom(x1, y1, random_width, random_height)
            place_room1 = check_room(
                RectangularRoom(x1 - 1, y1 - 1, random_width + 2, random_height + 1),
                dungeon,
            )

        if place_room1:
            break

    if place_room1:
        map_room(room1, dungeon)

    place_room2 = False
    room2 = room1
    if verticalLayout:
        room2 = RectangularRoom(
            area.x1 + area.width, room1.y1, room1.width, room1.height
        )

        place_room2 = check_room(
            RectangularRoom(room2.x1, room2.y1 - 1, room2.width + 1, room2.height + 2),
            dungeon,
        )
    else:
        room2 = RectangularRoom(
            room1.x1, area.y1 + area.height, room1.width, room1.height
        )

        place_room2 = check_room(
            RectangularRoom(room2.x1 - 1, room2.y1, room2.width + 2, room2.height + 1),
            dungeon,
        )

    if place_room2:
        map_room(room2, dungeon)
    if place_room1:
        generate_room(room1, dungeon, not verticalLayout)
    if place_room2:
        generate_room(room2, dungeon, not verticalLayout)


def first_room(dungeon: GameMap):
    print("First room")
    has_chamber1 = not flip_coin()
    has_chamber2 = not flip_coin()
    has_chamber3 = not flip_coin()

    if not has_chamber1 or not has_chamber3:
        has_chamber2 = True

    chamber1 = RectangularRoom(1, 15, 10, 10)
    chamber2 = RectangularRoom(15, 15, 10, 10)
    chamber3 = RectangularRoom(29, 15, 10, 10)
    hallway_x1 = 1
    hallway_width = 38
    if not has_chamber1:
        hallway_x1 += 17
        hallway_width -= 17
    if not has_chamber3:
        hallway_width -= 16

    hallway = RectangularRoom(hallway_x1, 17, hallway_width, 6)

    if has_chamber1:
        map_room(chamber1, dungeon)
    if has_chamber2:
        map_room(chamber2, dungeon)
    if has_chamber3:
        map_room(chamber3, dungeon)

    map_room(hallway, dungeon)

    if has_chamber1:
        generate_room(chamber1, dungeon, True)
    if has_chamber2:
        generate_room(chamber2, dungeon, True)
    if has_chamber3:
        generate_room(chamber3, dungeon, True)
