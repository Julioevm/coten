"""Generator of cathedral type maps."""

from __future__ import annotations
import copy

import random
from typing import TYPE_CHECKING, List, Tuple

import numpy as np

from map_gen import parameters

import tile_types
from game_map import GameMap
from map_gen.procgen import (
    get_max_value_for_floor,
)
from map_gen.rectangular_room import RectangularRoom
from utils import flip_coin, generate_rnd

if TYPE_CHECKING:
    from engine import Engine

Tile = {
    "Dirt": 0,
    "Floor": 1,
    "Corner": 2,
    "Wall": 3,
    "Arch": 4,
    "VWall": 5,
    "VWallEnd": 6,
    "HWall": 7,
    "HWallEnd": 8,
    "VCorner": 9,
    "HCorner": 10,
    "DirtHwall": 11,
    "DirtVwall": 12,
    "VDirtCorner": 13,
    "HDirtCorner": 14,
    "DirtHwallEnd": 15,
    "DirtVwallEnd": 16,
    "Pillar": 17,
    "HArch": 18,
    "VArch": 19,
    "HArchEnd": 20,
    "VArchEnd": 21,
    "HArchVWall": 22,
    "VArchHWall": 23,
    "HFence": 24,
    "HFenceVWall": 25,
    "HDoor": 26,
    "HDoorEnd": 27,
    "HWallVArch": 28,
    "Door": 29,
    "VFence": 30,
    "DWall": 31,
    "VDoor": 32,
    "DArch": 33,
    "HWallVFence": 34,
    "DirtHWall": 35,
    "DirtVWall": 36,
}

rooms: List[RectangularRoom] = []

dungeon_mask = np.array([])
protected = np.array([])
dungeon = np.array([])
chamber = np.array([])

vertical_layout = False

has_chamber1 = False
has_chamber2 = False
has_chamber3 = False

max_encounters = 0
current_encounters = 0
color_rooms = False

DMAXX = 0
DMAXY = 0

def init_dungeon_flags(map: GameMap):
    global dungeon
    global protected
    global chamber
    DMAXX = map.width
    DMAXY = map.height
    dungeon = np.full((DMAXX, DMAXY), fill_value=Tile["Dirt"], order="F")
    protected = np.full((DMAXX, DMAXY), fill_value=False, order="F")
    chamber = np.full((DMAXX, DMAXY), fill_value=False, order="F")


def get_min_area(level: int):
    if level < 5:
        return 530
    if level < 7:
        return 600
    if level < 9:
        return 710

    return 761


def generate_cathedral(
    map_width: int,
    map_height: int,
    engine: Engine,
) -> GameMap:
    global max_encounters, DMAXX, DMAXY
    player = engine.player
    map = GameMap(engine, map_width, map_height, entities=[player], name="Castle")
    DMAXX = map.width
    DMAXY = map.height
    floor = engine.game_world.current_floor
    max_encounters = get_max_value_for_floor(parameters.max_encounters_by_floor, floor)

    while True:
        while True:
            first_room(map)
            if find_area() > get_min_area(floor):
                break

        init_dungeon_flags(map)
        make_dmt()
        fill_chambers()
        fix_tiles_patterns()
        add_wall()

        map_dungeon(map)
        if place_all_stairs(map):
            break

    if player is not None:
        player.place(*map.downstairs_location, map)
    return map


def map_room(room: RectangularRoom, map: GameMap):
    global rooms
    global dungeon_mask
    rooms.append(room)

    for x, y in room.get_outer_points():
        if x > map.width - 1 or y > map.height - 1:
            continue
        dungeon_mask[x, y] = True


def place_stairs(map: GameMap, tile_type, location_name: str) -> bool:
    x = generate_rnd(map.width - 1)
    y = generate_rnd(map.height - 1)
    j = y
    for i in range(x, map.width - 1):
        if i == map.width - 1:
            i = 0
            j += 1
            if j == map.height - 1:
                j = 0
        if dungeon[i][j] == Tile["Floor"]:
            map.tiles[i][j] = tile_type
            setattr(map, location_name, (i, j))
            return True
    return False


def place_all_stairs(map: GameMap) -> bool:
    stairs_down = place_stairs(map, tile_types.down_stairs, "downstairs_location")
    stairs_up = place_stairs(map, tile_types.up_stairs, "upstairs_location")
    return stairs_down and stairs_up


def check_room(room: RectangularRoom, dungeon: GameMap):
    global rooms
    global dungeon_mask
    if (
        room.x < 0
        or room.y < 0
        or room.x2 >= dungeon.width
        or room.y2 >= dungeon.height
    ):
        return False

    for x, y in room.get_outer_points():
        if dungeon_mask[x][y]:
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
                    room1.x - 1, room1.y - 1, room1.width + 1, room1.height + 2
                ),
                dungeon,
            )
        else:
            room1.x += int(area.width / 2 - random_width / 2)
            room1.y += -room1.height
            place_room1 = check_room(
                RectangularRoom(
                    room1.x - 1, room1.y - 1, room1.width + 2, room1.height + 1
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
            RectangularRoom(room2.x1 + 1, room2.y1, room2.width + 1, room2.height + 2),
            dungeon,
        )
    else:
        room2.y = area.y + area.height

        place_room2 = check_room(
            RectangularRoom(room2.x1, room2.y1 + 1, room2.width + 2, room2.height + 1),
            dungeon,
        )

    if place_room2:
        map_room(room2, dungeon)
    if place_room1:
        generate_room(room1, dungeon, not vertical_layout)
    if place_room2:
        generate_room(room2, dungeon, not vertical_layout)


def first_room(map: GameMap):
    global rooms, dungeon_mask
    global vertical_layout, has_chamber1, has_chamber2, has_chamber3

    dungeon_mask = np.full((map.width, map.height), fill_value=False, order="F")
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
        map_room(chamber1, map)
    if has_chamber2:
        map_room(chamber2, map)
    if has_chamber3:
        map_room(chamber3, map)

    map_room(hallway, map)

    if has_chamber1:
        generate_room(chamber1, map, vertical_layout)
    if has_chamber2:
        generate_room(chamber2, map, vertical_layout)
    if has_chamber3:
        generate_room(chamber3, map, vertical_layout)


def find_area():
    global rooms
    total_count = 0
    for room in rooms:
        total_count += room.outer_size

    return total_count


def fill_chambers():
    global vertical_layout, has_chamber1, has_chamber2, has_chamber3
    chamber1 = (0, 14)
    chamber3 = (28, 14)
    hall1 = (12, 18)
    hall2 = (26, 18)

    if vertical_layout:
        chamber1 = (chamber1[1], chamber1[0])
        chamber3 = (chamber3[1], chamber3[0])
        hall1 = (hall1[1], hall1[0])
        hall2 = (hall2[1], hall2[0])

    if has_chamber1:
        generate_chamber(chamber1, False, True, vertical_layout)
    if has_chamber2:
        generate_chamber((14, 14), has_chamber1, has_chamber3, vertical_layout)
    if has_chamber3:
        generate_chamber(chamber3, True, False, vertical_layout)

    if has_chamber2:
        if has_chamber1:
            generate_hall(hall1, 2, vertical_layout)
        if has_chamber3:
            generate_hall(hall2, 2, vertical_layout)
    else:
        generate_hall(hall1, 16, vertical_layout)

        # InitSetPiece()
        # Set a set piece in one of the chambers


def fix_tiles_patterns():
    for j in range(DMAXY):
        for i in range(DMAXX):
            if i + 1 < DMAXX:
                if dungeon[i][j] == Tile["HWall"] and dungeon[i + 1][j] == Tile["Dirt"]:
                    dungeon[i + 1][j] = Tile["DirtHwallEnd"]
                if dungeon[i][j] == Tile["Floor"] and dungeon[i + 1][j] == Tile["Dirt"]:
                    dungeon[i + 1][j] = Tile["DirtHwall"]
                if (
                    dungeon[i][j] == Tile["Floor"]
                    and dungeon[i + 1][j] == Tile["HWall"]
                ):
                    dungeon[i + 1][j] = Tile["HWallEnd"]
                if (
                    dungeon[i][j] == Tile["VWallEnd"]
                    and dungeon[i + 1][j] == Tile["Dirt"]
                ):
                    dungeon[i + 1][j] = Tile["DirtVwallEnd"]

            if j + 1 < DMAXY:
                if dungeon[i][j] == Tile["VWall"] and dungeon[i][j + 1] == Tile["Dirt"]:
                    dungeon[i][j + 1] = Tile["DirtVwallEnd"]
                if (
                    dungeon[i][j] == Tile["Floor"]
                    and dungeon[i][j + 1] == Tile["VWall"]
                ):
                    dungeon[i][j + 1] = Tile["VWallEnd"]
                if dungeon[i][j] == Tile["Floor"] and dungeon[i][j + 1] == Tile["Dirt"]:
                    dungeon[i][j + 1] = Tile["DirtVwall"]

    for j in range(DMAXY):
        for i in range(DMAXX):
            if i + 1 < DMAXX:
                if (
                    dungeon[i][j] == Tile["Floor"]
                    and dungeon[i + 1][j] == Tile["DirtVwall"]
                ):
                    dungeon[i + 1][j] = Tile["HDirtCorner"]
                if dungeon[i][j] == Tile["Floor"] and dungeon[i + 1][j] == Tile["Dirt"]:
                    dungeon[i + 1][j] = Tile["VDirtCorner"]
                if (
                    dungeon[i][j] == Tile["HWallEnd"]
                    and dungeon[i + 1][j] == Tile["Dirt"]
                ):
                    dungeon[i + 1][j] = Tile["DirtHwallEnd"]
                if (
                    dungeon[i][j] == Tile["Floor"]
                    and dungeon[i + 1][j] == Tile["DirtVwallEnd"]
                ):
                    dungeon[i + 1][j] = Tile["HDirtCorner"]
                if (
                    dungeon[i][j] == Tile["DirtVwall"]
                    and dungeon[i + 1][j] == Tile["Dirt"]
                ):
                    dungeon[i + 1][j] = Tile["VDirtCorner"]
                if (
                    dungeon[i][j] == Tile["HWall"]
                    and dungeon[i + 1][j] == Tile["DirtVwall"]
                ):
                    dungeon[i + 1][j] = Tile["HDirtCorner"]
                if (
                    dungeon[i][j] == Tile["DirtVwall"]
                    and dungeon[i + 1][j] == Tile["VWall"]
                ):
                    dungeon[i + 1][j] = Tile["VWallEnd"]
                if (
                    dungeon[i][j] == Tile["HWallEnd"]
                    and dungeon[i + 1][j] == Tile["DirtVwall"]
                ):
                    dungeon[i + 1][j] = Tile["HDirtCorner"]
                if (
                    dungeon[i][j] == Tile["HWall"]
                    and dungeon[i + 1][j] == Tile["VWall"]
                ):
                    dungeon[i + 1][j] = Tile["VWallEnd"]
                if (
                    dungeon[i][j] == Tile["Corner"]
                    and dungeon[i + 1][j] == Tile["Dirt"]
                ):
                    dungeon[i + 1][j] = Tile["DirtVwallEnd"]
                if (
                    dungeon[i][j] == Tile["HDirtCorner"]
                    and dungeon[i + 1][j] == Tile["VWall"]
                ):
                    dungeon[i + 1][j] = Tile["VWallEnd"]
                if (
                    dungeon[i][j] == Tile["HWallEnd"]
                    and dungeon[i + 1][j] == Tile["VWall"]
                ):
                    dungeon[i + 1][j] = Tile["VWallEnd"]
                if (
                    dungeon[i][j] == Tile["HWallEnd"]
                    and dungeon[i + 1][j] == Tile["DirtVwallEnd"]
                ):
                    dungeon[i + 1][j] = Tile["HDirtCorner"]
                if (
                    dungeon[i][j] == Tile["DWall"]
                    and dungeon[i + 1][j] == Tile["VCorner"]
                ):
                    dungeon[i + 1][j] = Tile["HCorner"]
                if (
                    dungeon[i][j] == Tile["HWallEnd"]
                    and dungeon[i + 1][j] == Tile["Floor"]
                ):
                    dungeon[i + 1][j] = Tile["HCorner"]
                if (
                    dungeon[i][j] == Tile["HWall"]
                    and dungeon[i + 1][j] == Tile["DirtVwallEnd"]
                ):
                    dungeon[i + 1][j] = Tile["HDirtCorner"]
                if (
                    dungeon[i][j] == Tile["HWall"]
                    and dungeon[i + 1][j] == Tile["Floor"]
                ):
                    dungeon[i + 1][j] = Tile["HCorner"]
            if i > 0:
                if (
                    dungeon[i][j] == Tile["DirtHwallEnd"]
                    and dungeon[i - 1][j] == Tile["Dirt"]
                ):
                    dungeon[i - 1][j] = Tile["DirtVwall"]
                if dungeon[i][j] == ["DirtVwall"] and dungeon[i - 1][j] == [
                    "DirtHwallEnd"
                ]:
                    dungeon[i - 1][j] = ["HDirtCorner"]
                if dungeon[i][j] == ["VWallEnd"] and dungeon[i - 1][j] == ["Dirt"]:
                    dungeon[i - 1][j] = ["DirtVwallEnd"]
                if dungeon[i][j] == ["VWallEnd"] and dungeon[i - 1][j] == [
                    "DirtHwallEnd"
                ]:
                    dungeon[i - 1][j] = ["HDirtCorner"]
            if j + 1 < DMAXY:
                if (
                    dungeon[i][j] == Tile["VWall"]
                    and dungeon[i][j + 1] == Tile["HWall"]
                ):
                    dungeon[i][j + 1] = Tile["HWallEnd"]
                if (
                    dungeon[i][j] == Tile["VWallEnd"]
                    and dungeon[i][j + 1] == Tile["DirtHwall"]
                ):
                    dungeon[i][j + 1] = Tile["HDirtCorner"]
                if (
                    dungeon[i][j] == Tile["DirtHwall"]
                    and dungeon[i][j + 1] == Tile["HWall"]
                ):
                    dungeon[i][j + 1] = Tile["HWallEnd"]
                if (
                    dungeon[i][j] == Tile["VWallEnd"]
                    and dungeon[i][j + 1] == Tile["HWall"]
                ):
                    dungeon[i][j + 1] = Tile["HWallEnd"]
                if (
                    dungeon[i][j] == Tile["HDirtCorner"]
                    and dungeon[i][j + 1] == Tile["HWall"]
                ):
                    dungeon[i][j + 1] = Tile["HWallEnd"]
                if (
                    dungeon[i][j] == Tile["VWallEnd"]
                    and dungeon[i][j + 1] == Tile["Dirt"]
                ):
                    dungeon[i][j + 1] = Tile["DirtVwallEnd"]
                if (
                    dungeon[i][j] == Tile["VWallEnd"]
                    and dungeon[i][j + 1] == Tile["Floor"]
                ):
                    dungeon[i][j + 1] = Tile["VCorner"]
                if (
                    dungeon[i][j] == Tile["VWall"]
                    and dungeon[i][j + 1] == Tile["Floor"]
                ):
                    dungeon[i][j + 1] = Tile["VCorner"]
                if (
                    dungeon[i][j] == Tile["Floor"]
                    and dungeon[i][j + 1] == Tile["VCorner"]
                ):
                    dungeon[i][j + 1] = Tile["HCorner"]
            if j > 0:
                if (
                    dungeon[i][j] == Tile["VWallEnd"]
                    and dungeon[i][j - 1] == Tile["Dirt"]
                ):
                    dungeon[i][j - 1] = Tile["HWallEnd"]
                if (
                    dungeon[i][j] == Tile["VWallEnd"]
                    and dungeon[i][j - 1] == Tile["Dirt"]
                ):
                    dungeon[i][j - 1] = Tile["DirtVwallEnd"]
                if (
                    dungeon[i][j] == Tile["HWallEnd"]
                    and dungeon[i][j - 1] == Tile["DirtVwallEnd"]
                ):
                    dungeon[i][j - 1] = Tile["HDirtCorner"]
                if (
                    dungeon[i][j] == Tile["DirtHwall"]
                    and dungeon[i][j - 1] == Tile["DirtVwallEnd"]
                ):
                    dungeon[i][j - 1] = Tile["HDirtCorner"]

    for j in range(DMAXY):
        for i in range(DMAXX):
            if (
                j + 1 < DMAXY
                and dungeon[i][j] == Tile["DWall"]
                and dungeon[i][j + 1] == Tile["HWall"]
            ):
                dungeon[i][j + 1] = Tile["HWallEnd"]
            if (
                i + 1 < DMAXX
                and dungeon[i][j] == Tile["HWall"]
                and dungeon[i + 1][j] == Tile["DirtVWall"]
            ):
                dungeon[i + 1][j] = Tile["HDirtCorner"]
            if (
                j + 1 < DMAXY
                and dungeon[i][j] == Tile["DirtHWall"]
                and dungeon[i][j + 1] == Tile["Dirt"]
            ):
                dungeon[i + 1][j] = Tile["VDirtCorner"]


def make_dmt():
    global dungeon
    global dungeon_mask

    for j in range(DMAXY - 1):
        for i in range(DMAXX - 1):
            if dungeon_mask[i][j]:
                dungeon[i][j] = Tile["Floor"]
            elif (
                not dungeon_mask[i + 1][j + 1]
                and dungeon_mask[i][j + 1]
                and dungeon_mask[i + 1, j]
            ):
                dungeon[i][j] = Tile["Floor"]  # Remove diagonal corners
            elif (
                dungeon_mask[i + 1][j + 1]
                and dungeon_mask[i][j + 1]
                and dungeon_mask[i + 1][j]
            ):
                dungeon[i][j] = Tile["VCorner"]
            elif dungeon_mask[i][j + 1]:
                dungeon[i][j] = Tile["HWall"]
            elif dungeon_mask[i + 1][j]:
                dungeon[i][j] = Tile["VWall"]
            elif dungeon_mask[i + 1][j + 1]:
                dungeon[i][j] = Tile["DWall"]
            else:
                dungeon[i][j] = Tile["Dirt"]


def generate_hall(start, length, verticalLayout):
    if verticalLayout:
        for i in range(start[1], start[1] + length):
            dungeon[start[0]][i] = Tile["Arch"]
            dungeon[start[0] + 3][i] = Tile["Arch"]
    else:
        for i in range(start[0], start[0] + length):
            dungeon[i][start[1]] = Tile["Arch"]
            dungeon[i][start[1] + 3] = Tile["Arch"]


def generate_chamber(
    position: Tuple[int, int], connectPrevious, connectNext, verticalLayout
):
    global dungeon, chamber
    x, y = position
    if connectPrevious:
        if verticalLayout:
            dungeon[x + 2][y] = Tile["HWall"]
            dungeon[x + 3][y] = Tile["HArch"]
            dungeon[x + 4][y] = Tile["Pillar"]
            dungeon[x + 7][y] = Tile["Pillar"]
            dungeon[x + 8][y] = Tile["HArch"]
            dungeon[x + 9][y] = Tile["HWall"]
        else:
            dungeon[x][y + 2] = Tile["VWall"]
            dungeon[x][y + 3] = Tile["VArch"]
            dungeon[x][y + 4] = Tile["Pillar"]
            dungeon[x][y + 7] = Tile["Pillar"]
            dungeon[x][y + 8] = Tile["VArch"]
            dungeon[x][y + 9] = Tile["VWall"]

    if connectNext:
        if verticalLayout:
            y += 11
            dungeon[x + 2][y] = Tile["HWall"]
            dungeon[x + 3][y] = Tile["HArch"]
            dungeon[x + 4][y] = Tile["Pillar"]
            dungeon[x + 7][y] = Tile["Pillar"]
            dungeon[x + 8][y] = Tile["HArch"]

            if dungeon[x + 9][y] != Tile["DWall"]:
                dungeon[x + 9][y] = Tile["HDirtCorner"]
            y -= 11
        else:
            x += 11
            dungeon[x][y + 2] = Tile["HWallVArch"]
            dungeon[x][y + 3] = Tile["VArch"]
            dungeon[x][y + 4] = Tile["Pillar"]
            dungeon[x][y + 7] = Tile["Pillar"]
            dungeon[x][y + 8] = Tile["VArch"]

            if dungeon[x][y + 9] != Tile["DWall"]:
                dungeon[x][y + 9] = Tile["HDirtCorner"]
            x -= 11

    for i in range(1, 11):
        for j in range(1, 11):
            dungeon[j + x][i + y] = Tile["Floor"]
            chamber[j + x][i + y] = True

    dungeon[x + 4][y + 4] = Tile["Pillar"]
    dungeon[x + 7][y + 4] = Tile["Pillar"]
    dungeon[x + 4][y + 7] = Tile["Pillar"]
    dungeon[x + 7][y + 7] = Tile["Pillar"]


def HorizontalWallOk(position: Tuple[int, int]):
    global protected
    global chamber
    length = 1
    x, y = position
    while dungeon[x + length][y] == Tile["Floor"]:
        if (
            dungeon[x + length][y - 1] != Tile["Floor"]
            or dungeon[x + length][y + 1] != Tile["Floor"]
            or protected[x + length][y]
            or chamber[x + length][y]
        ):
            break
        length += 1

    if length == 1:
        return -1

    tileId = dungeon[x + length][y]

    if tileId not in (
        Tile["Corner"],
        Tile["Wall"],
        Tile["Arch"],
        Tile["VWallEnd"],
        Tile["HWallEnd"],
        Tile["VCorner"],
        Tile["HCorner"],
        Tile["DirtHwall"],
        Tile["DirtVwall"],
        Tile["VDirtCorner"],
        Tile["HDirtCorner"],
        Tile["DirtHwallEnd"],
        Tile["DirtVwallEnd"],
    ):
        return -1

    return length


def VerticalWallOk(position):
    global protected, chamber
    x, y = position
    length = 1
    while dungeon[x][y + length] == Tile["Floor"]:
        if (
            dungeon[x - 1][y + length] != Tile["Floor"]
            or dungeon[x + 1][y + length] != Tile["Floor"]
            or protected[x][y + length]
            or chamber[x][y + length]
        ):
            break
        length += 1

    if length == 1:
        return -1

    tile_id = dungeon[x][y + length]

    if tile_id not in (
        Tile["Corner"],
        Tile["Wall"],
        Tile["Arch"],
        Tile["VWallEnd"],
        Tile["HWallEnd"],
        Tile["VCorner"],
        Tile["HCorner"],
        Tile["DirtHwall"],
        Tile["DirtVwall"],
        Tile["VDirtCorner"],
        Tile["HDirtCorner"],
        Tile["DirtHwallEnd"],
        Tile["DirtVwallEnd"],
    ):
        return -1

    return length


def HorizontalWall(position: Tuple[int, int], start: int, maxX: int):
    global protected
    x, y = position
    wallTile = Tile["HWall"]
    doorTile = Tile["HDoor"]

    rnd = generate_rnd(4)
    if rnd == 2:  # Add arch
        wallTile = Tile["HArch"]
        doorTile = Tile["HArch"]
        if start == Tile["HWall"]:
            start = Tile["HArch"]
        elif start == Tile["DWall"]:
            start = Tile["HArchVWall"]
    elif rnd == 3:  # Add Fence
        wallTile = Tile["HFence"]
        if start == Tile["HWall"]:
            start = Tile["HFence"]
        elif start == Tile["DWall"]:
            start = Tile["HFenceVWall"]

    if generate_rnd(6) == 5:
        doorTile = Tile["HArch"]

    dungeon[x][y] = start

    for i in range(1, maxX):
        dungeon[x + i][y] = wallTile

    i = generate_rnd(maxX - 1) + 1

    dungeon[x + i][y] = doorTile

    if doorTile == Tile["HDoor"]:
        protected[x + i][y] = True


def VerticalWall(position, start, max_y):
    x, y = position
    wall_tile = Tile["VWall"]
    door_tile = Tile["VDoor"]

    rnd = generate_rnd(4)
    if rnd == 2:  # Add arch
        wall_tile = Tile["VArch"]
        door_tile = Tile["VArch"]
        if start == Tile["VWall"]:
            start = Tile["VArch"]
        elif start == Tile["DWall"]:
            start = Tile["HWallVArch"]
    elif rnd == 3:  # Add Fence
        wall_tile = Tile["VFence"]
        if start == Tile["VWall"]:
            start = Tile["VFence"]
        elif start == Tile["DWall"]:
            start = Tile["HWallVFence"]

    if generate_rnd(6) == 5:
        door_tile = Tile["VArch"]

    dungeon[x][y] = start

    for j in range(1, max_y):
        dungeon[x][y + j] = wall_tile

    j = generate_rnd(max_y - 1) + 1

    dungeon[x][y + j] = door_tile
    if door_tile == Tile["VDoor"]:
        protected[x][y + j] = True


def add_wall():
    global protected
    global chamber
    global dungeon

    for j in range(DMAXY):
        for i in range(DMAXX):
            if protected[i][j] or chamber[i][j]:
                continue

            if dungeon[i][j] == Tile["Corner"]:
                max_x = HorizontalWallOk((i, j))
                if max_x != -1:
                    HorizontalWall((i, j), Tile["HWall"], max_x)

            if dungeon[i][j] == Tile["Corner"]:
                max_y = VerticalWallOk((i, j))
                if max_y != -1:
                    VerticalWall((i, j), Tile["VWall"], max_y)

            if dungeon[i][j] == Tile["VWallEnd"]:
                max_x = HorizontalWallOk((i, j))
                if max_x != -1:
                    HorizontalWall((i, j), Tile["DWall"], max_x)

            if dungeon[i][j] == Tile["HWallEnd"]:
                max_y = VerticalWallOk((i, j))
                if max_y != -1:
                    VerticalWall((i, j), Tile["DWall"], max_y)

            if dungeon[i][j] == Tile["HWall"]:
                max_x = HorizontalWallOk((i, j))
                if max_x != -1:
                    HorizontalWall((i, j), Tile["HWall"], max_x)

            if dungeon[i][j] == Tile["VWall"]:
                max_y = VerticalWallOk((i, j))
                if max_y != -1:
                    VerticalWall((i, j), Tile["VWall"], max_y)


def map_dungeon(map: GameMap):
    global dungeon
    # iterate through the dungeon tiles
    # map the dungeon tiles to the corresponding tile type
    for j in range(map.height):
        for i in range(map.width):
            if dungeon[i][j] == Tile["Floor"]:
                map.tiles[i][j] = tile_types.floor
            elif dungeon[i][j] in (
                Tile["Wall"],
                Tile["DWall"],
                Tile["VWall"],
                Tile["HWall"],
                Tile["VWallEnd"],
                Tile["HWallEnd"],
                Tile["VCorner"],
                Tile["HCorner"],
                Tile["VArchHWall"],
                Tile["HWallVArch"],
                Tile["DirtHwall"],
                Tile["DirtVwall"],
                Tile["VDirtCorner"],
                Tile["HDirtCorner"],
                Tile["DirtHwallEnd"],
                Tile["DirtVwallEnd"],
                Tile["HWallVFence"],
                Tile["HFenceVWall"],
                Tile["HArchVWall"],
            ):
                map.tiles[i][j] = tile_types.wall
            elif dungeon[i][j] in (
                Tile["Arch"],
                Tile["VArch"],
                Tile["HArch"],
                Tile["DArch"],
                Tile["Corner"],
                Tile["VArchEnd"],
                Tile["HArchEnd"],
                Tile["DirtVwall"],
            ):
                map.tiles[i][j] = tile_types.arch
            elif dungeon[i][j] in (Tile["HFence"], Tile["VFence"]):
                map.tiles[i][j] = tile_types.fence
            elif dungeon[i][j] == Tile["Pillar"]:
                map.tiles[i][j] = tile_types.pillar
            elif dungeon[i][j] in (Tile["HDoor"], Tile["VDoor"]):
                map.tiles[i][j] = tile_types.closed_door
            elif dungeon[i][j] == Tile["Dirt"]:
                map.tiles[i][j] = tile_types.wall
            else:
                map.tiles[i][j] = tile_types.unknown
