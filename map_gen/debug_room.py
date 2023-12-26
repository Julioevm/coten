from copy import deepcopy
from game_map import GameMap
from map_gen.rectangular_room import RectangularRoom
import tile_types
import item_factories

from engine import Engine


def create_debug_room(map_width: int, map_height: int, engine: Engine) -> GameMap:
    """Create a debug room."""
    player = engine.player
    room_width = 30
    room_height = 20
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    new_room = RectangularRoom(map_width // 2, map_height // 2, room_width, room_height)

    # Set all tiles in the room to floor tiles
    dungeon.tiles[new_room.inner] = tile_types.floor

    # Place some items
    fireball_scroll = deepcopy(item_factories.fireball_scroll)
    fireball_scroll.place(new_room.x1 + 3, new_room.y1 + 1, dungeon)

    holy_water = deepcopy(item_factories.holy_water_vial)
    holy_water.place(new_room.x1 + 1, new_room.y1 + 2, dungeon)

    player.place(*new_room.center, dungeon)

    dungeon.tiles[new_room.center] = tile_types.up_stairs
    dungeon.upstairs_location = new_room.center
    return dungeon
