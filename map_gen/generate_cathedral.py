"""Generator of cathedral type maps."""

from __future__ import annotations
import copy

import random
from typing import TYPE_CHECKING, List

from map_gen import parameters

import tile_types
from game_map import GameMap
from map_gen.procgen import (
    get_max_value_for_floor,
)
from map_gen.rectangular_room import RectangularRoom
from utils import generate_random_rgb

if TYPE_CHECKING:
    from engine import Engine

rooms: List[RectangularRoom] = []
max_encounters = 0
current_encounters = 0


def flip_coin(times=1):
    flip = False
    for _ in range(times):
        flip = random.choice([True, False])
    return flip


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

    print(find_area())
    return dungeon


def map_room(room: RectangularRoom, dungeon: GameMap):
    global rooms
    rooms.append(room)
    room_color = generate_random_rgb()

    for x, y in room.get_outer_points():
        if x > dungeon.width - 1 or y > dungeon.height - 1:
            continue
        dungeon.tiles[x, y] = tile_types.floor

        # dungeon.tiles[x, y] = tile_types.new_tile(
        #     walkable=True,
        #     transparent=True,
        #     dark=(ord(" "), (255, 255, 255), (22, 24, 43)),
        #     light=(ord(" "), (255, 255, 255), room_color),
        # )


def check_room(room: RectangularRoom, dungeon: GameMap):
    global rooms
    if room.x < 0 or room.y < 0 or room.x2 > dungeon.width or room.y2 > dungeon.height:
        return False

    if any(room.intersects(other_room) for other_room in rooms):
        return False

    return True


def generate_room(area: RectangularRoom, dungeon: GameMap, vertical_layout: bool):
    place_room1 = False

    rotate = flip_coin(4)
    vertical_layout = (not vertical_layout and rotate) or (
        vertical_layout and not rotate
    )

    room1 = RectangularRoom(0, 0, 0, 0)

    for _ in range(20):
        random_width = (random.randint(0, 4) + 2) & ~1
        random_height = (random.randint(0, 4) + 2) & ~1
        room1.x = area.x
        room1.y = area.y
        room1.width = random_width
        room1.height = random_height

        if vertical_layout:
            room1.x += -room1.width
            room1.y += int(area.height / 2 - room1.height / 2)
            place_room1 = check_room(
                RectangularRoom(
                    room1.x - 1, room1.y - 1, room1.width, room1.height + 1
                ),
                dungeon,
            )
        else:
            room1.x += int(area.width / 2 - random_width / 2)
            room1.y += -room1.height
            place_room1 = check_room(
                RectangularRoom(
                    room1.x - 1, room1.y - 1, room1.width + 1, room1.height
                ),
                dungeon,
            )

        if place_room1:
            break

    if place_room1:
        map_room(room1, dungeon)

    place_room2 = False
    room2 = copy.deepcopy(room1)

    if vertical_layout:
        room2.x = area.x + area.width

        place_room2 = check_room(
            RectangularRoom(room2.x1 + 1, room2.y1, room2.width, room2.height + 1),
            dungeon,
        )
    else:
        room2.y = area.y + area.height

        place_room2 = check_room(
            RectangularRoom(room2.x1, room2.y1 + 1, room2.width + 1, room2.height),
            dungeon,
        )

    if place_room2:
        map_room(room2, dungeon)
    if place_room1:
        generate_room(room1, dungeon, not vertical_layout)
    if place_room2:
        generate_room(room2, dungeon, not vertical_layout)


def first_room(dungeon: GameMap):
    global rooms
    rooms = []
    vertical_layout = flip_coin()
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

    if vertical_layout:
        chamber1.x, chamber1.y = chamber1.y, chamber1.x
        chamber3.x, chamber3.y = chamber3.y, chamber3.x
        hallway.x, hallway.y = hallway.y, hallway.x
        hallway.width, hallway.height = hallway.height, hallway.width

    if has_chamber1:
        map_room(chamber1, dungeon)
    if has_chamber2:
        map_room(chamber2, dungeon)
    if has_chamber3:
        map_room(chamber3, dungeon)

    map_room(hallway, dungeon)

    if has_chamber1:
        generate_room(chamber1, dungeon, vertical_layout)
    if has_chamber2:
        generate_room(chamber2, dungeon, vertical_layout)
    if has_chamber3:
        generate_room(chamber3, dungeon, vertical_layout)


def find_area():
    global rooms
    total_count = 0
    for room in rooms:
        total_count += room.outer_size

    return total_count
