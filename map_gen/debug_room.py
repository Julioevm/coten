from copy import deepcopy
from game_map import GameMap
from map_gen.rectangular_room import RectRoom
import tile_types
import item_factories

from engine import Engine


def create_debug_room(map_width: int, map_height: int, engine: Engine) -> GameMap:
    """Create a debug room."""
    player = engine.player
    room_width = 30
    room_height = 20
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    new_room = RectRoom(map_width // 2, map_height // 2, room_width, room_height)

    # Set all tiles in the room to floor tiles
    dungeon.tiles[new_room.inner] = tile_types.floor

    # Place some items
    confusion_scroll = deepcopy(item_factories.confusion_scroll)
    confusion_scroll.place(new_room.x1 + 3, new_room.y1 + 1, dungeon)

    map_item = deepcopy(item_factories.map_scroll)
    map_item.place(new_room.x1 + 4, new_room.y1 + 1, dungeon)

    holy_water = deepcopy(item_factories.holy_water_vial)
    holy_water.place(new_room.x1 + 1, new_room.y1 + 2, dungeon)

    bow = deepcopy(item_factories.bow)
    bow.place(new_room.x1 + 12, new_room.y1 + 12, dungeon)

    crossbow = deepcopy(item_factories.crossbow)
    crossbow.place(new_room.x1 + 13, new_room.y1 + 12, dungeon)

    arrows = deepcopy(item_factories.arrows)
    arrows.place(new_room.x1 + 14, new_room.y1 + 14, dungeon)

    bolts = deepcopy(item_factories.bolts)
    bolts.place(new_room.x1 + 16, new_room.y1 + 16, dungeon)

    player.place(*new_room.center, dungeon)

    dungeon.tiles[new_room.center] = tile_types.up_stairs
    dungeon.upstairs_location = new_room.center
    return dungeon
