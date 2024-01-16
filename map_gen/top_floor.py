from copy import deepcopy
from game_map import GameMap
from map_gen.ellipsis_room import EllipsisRoom
import tile_types

from engine import Engine


def create_top_floor(map_width: int, map_height: int, engine: Engine) -> GameMap:
    """Create the top level of the castle."""
    player = engine.player
    room_width = 31
    game_map = GameMap(engine, map_width, map_height, entities=[player])

    new_room = EllipsisRoom(
        map_width // 2 - room_width // 2,
        map_height // 2 - room_width // 2,
        room_width,
        room_width,
    )

    # Set all tiles in the room to floor tiles
    for x, y in new_room.get_inner_points():
        game_map.tiles[x, y] = tile_types.floor

    player.place(*new_room.center, game_map)

    game_map.tiles[new_room.center] = tile_types.down_stairs
    game_map.downstairs_location = new_room.center
    return game_map
