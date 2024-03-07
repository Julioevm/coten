"Generator of interior type maps."

from typing import List

import numpy as np
import tile_types
from engine import Engine
from game_map import GameMap
from map_gen import parameters
from map_gen.procgen import get_max_value_for_floor
from map_gen.rectangular_room import RectRoom
from utils import generate_rnd


rooms: List[RectRoom] = []

dungeon_mask = np.array([])

max_encounters = 0
current_encounters = 0
color_rooms = False

DMAXX = 0
DMAXY = 0

Tile = {
    "Void": 0,
    "Wall": 1,
    "Door": 2,
    "Floor": 3,
    "Room": 4,
}


def generate_interior(
    map_width: int,
    map_height: int,
    engine: Engine,
) -> GameMap:
    global max_encounters, DMAXX, DMAXY, dungeon, dungeon_mask
    player = engine.player
    map = GameMap(engine, map_width, map_height, entities=[player], name="Castle")
    DMAXX = map.width
    DMAXY = map.height
    floor = engine.game_world.current_floor
    max_encounters = get_max_value_for_floor(parameters.max_encounters_by_floor, floor)
    dungeon_mask = np.full((map.width, map.height), fill_value=False, order="F")
    dungeon = np.full((DMAXX, DMAXY), fill_value=Tile["Void"], order="F")

    generate_halls(map)
    map_dungeon(map)
    place_doors(map)

    return map


def generate_halls(map: GameMap):

    hall_width = 4

    h_hall = RectRoom(1, map.height // 2 - 1, map.width - 2, hall_width)
    v_hall = RectRoom(map.width // 2 - 1, 1, hall_width, map.height - 2)

    nw_area = RectRoom(0, 0, map.width // 2 - 1, map.height // 2 - 1)
    ne_area = RectRoom(
        map.width // 2 + hall_width - 1,
        0,
        map.width // 2 - hall_width,
        map.height // 2 - hall_width,
    )
    sw_area = RectRoom(
        0,
        map.height // 2 + hall_width - 1,
        map.width // 2 - hall_width,
        map.height // 2 - hall_width,
    )
    se_area = RectRoom(
        map.width // 2 + hall_width - 1,
        map.height // 2 + hall_width - 1,
        map.width // 2 - hall_width - 1,
        map.height // 2 - hall_width,
    )

    map_room(h_hall, map)
    map_room(v_hall, map)

    split_area(nw_area, map)
    split_area(ne_area, map)
    split_area(sw_area, map)
    split_area(se_area, map)


def place_doors(map: GameMap):
    for room in rooms:
        map.place_door(room)


def map_room(room: RectRoom, map: GameMap):
    global rooms
    global dungeon_mask
    rooms.append(room)

    for x, y in room.get_inner_points():
        if x > map.width - 1 or y > map.height - 1:
            continue
        dungeon[x, y] = Tile["Floor"]


def map_dungeon(map: GameMap):
    global dungeon
    # iterate through the dungeon tiles
    # map the dungeon tiles to the corresponding tile type
    for j in range(DMAXY):
        for i in range(DMAXX):
            if dungeon[i][j] == Tile["Floor"]:
                map.tiles[i][j] = tile_types.floor


def split_area(area: RectRoom, map: GameMap):

    min_offset = 4
    if area.size < 26:
        map_room(area, map)
        return

    if area.width > area.height:
        # split horizontally
        split = generate_rnd(area.width - min_offset) + min_offset
        room1 = RectRoom(area.x1, area.y1, split, area.height)
        room2 = RectRoom(area.x1 + split, area.y1, area.width - split, area.height)
    else:
        # split vertically
        split = generate_rnd(area.height - min_offset) + min_offset
        room1 = RectRoom(area.x1, area.y1, area.width, split)
        room2 = RectRoom(area.x1, area.y1 + split, area.width, area.height - split)

    split_area(room1, map)
    split_area(room2, map)
