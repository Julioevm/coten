from typing import TYPE_CHECKING, List
from debug_room import create_debug_room
from exceptions import Impossible
from procgen import generate_dungeon

from engine import Engine

if TYPE_CHECKING:
    from game_map import GameMap


class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs.
    """

    def __init__(
        self,
        *,
        engine: Engine,
        map_width: int,
        map_height: int,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        current_floor: int = 0,
    ):
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.current_floor = current_floor

        self.floors: List[GameMap] = []

    def generate_floor(self) -> None:
        self.current_floor += 1
        game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            engine=self.engine,
        )

        self.floors.append(game_map)
        self.engine.game_map = game_map

    def load_prefab_map(self, map_name: str) -> None:
        self.current_floor += 1
        game_map = create_debug_room(
            map_width=self.map_width, map_height=self.map_height, engine=self.engine
        )
        self.floors.append(game_map)
        self.engine.game_map = game_map
        self.engine.game_map.reveal_map()

    def load_floor(self, floor: int) -> None:
        """
        Loads a specific floor of the game map. Use actual floor numbers, 1 to N.
        """

        # Throw an error if the floor does not exist

        if floor < 1 or floor > len(self.floors):
            raise Impossible("Invalid floor number")
        self.current_floor = floor
        self.engine.game_map = self.floors[floor - 1]
        self.engine.player.place(
            self.engine.game_map.upstairs_location[0],
            self.engine.game_map.upstairs_location[1],
            self.engine.game_map,
        )