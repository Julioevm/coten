from __future__ import annotations
from typing import TYPE_CHECKING, List

import utils
from engine import Engine
from exceptions import Impossible
import color
from map_gen import procgen
from map_gen.debug_room import create_debug_room
from map_gen.generate_cave import generate_cave
from map_gen.generate_dungeon import generate_dungeon
from map_gen.top_floor import create_top_floor
from map_gen.generate_cathedral import generate_cathedral

if TYPE_CHECKING:
    from game_map import GameMap

prefab_maps = {
    "debug_room": create_debug_room,
    "top_floor": create_top_floor,
}

world_prefabs = {
    10: "top_floor",
}

floor_map_generator = {
    0: lambda **kwargs: generate_cave(
        max_rooms=8, room_min_size=6, room_max_size=10, **kwargs
    ),
    1: lambda **kwargs: generate_cave(
        max_rooms=12, room_min_size=8, room_max_size=12, **kwargs
    ),
    4: lambda **kwargs: generate_dungeon(
        max_rooms=16, room_min_size=6, room_max_size=10, **kwargs
    ),
    6: lambda **kwargs: generate_cathedral(**kwargs),
    # Add more floors and corresponding functions with parameters as needed.
}


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
        current_floor: int = 1,
    ):
        self.engine = engine
        self.map_width = map_width
        self.map_height = map_height
        self.current_floor = current_floor
        self.floors: List[GameMap] = []

    def set_fixed_items(self, items) -> None:
        items = list(items)
        fixed_items = procgen.get_fixed_items(self.current_floor)

        # replace some items with the items in fixed_items if there are any
        if len(fixed_items) > 0:
            utils.replace_items_in_list(items, 0, fixed_items)

    def generate_floor(self) -> None:
        """Generate a new floor, using the corresponding floor generator function."""
        if self.engine.debug_mode:
            print(f"Generating floor {self.current_floor}")
        floor_generator = None
        for floor in sorted(floor_map_generator.keys(), reverse=True):
            if self.current_floor >= floor:
                floor_generator = floor_map_generator[floor]
                break

        # If no generator is found, default to generate_dungeon
        if floor_generator is None:
            floor_generator = generate_dungeon

        additional_params = {
            "map_width": self.map_width,
            "map_height": self.map_height,
            "engine": self.engine,
        }
        # Generate the game map using the chosen generator function
        game_map = floor_generator(**additional_params)

        self.set_fixed_items(game_map.items)

        self.floors.append(game_map)
        self.engine.game_map = game_map

    def load_prefab_map(self, map_name: str) -> None:
        params = {
            "map_width": self.map_width,
            "map_height": self.map_height,
            "engine": self.engine,
        }

        map_generator = prefab_maps[map_name]

        if map_generator is None:
            raise Impossible(f"Prefab map {map_name} not found!")

        game_map = map_generator(**params)
        self.floors.append(game_map)
        self.engine.game_map = game_map

    def load_floor(self, floor: int) -> None:
        """
        Loads a specific floor of the game map. Use actual floor numbers, 1 to N.
        """

        # Throw an error if the floor does not exist

        if floor < 1 or floor > len(self.floors):
            raise Impossible("Invalid floor number")

        if self.engine.debug_mode:
            print(f"Loading floor {floor}")

        # Update current loaded floor with the new floor
        self.engine.game_map = self.floors[floor - 1]

        # Set the pair of stairs to put the player on depending if we're ascending or descending
        stairs = (
            self.engine.game_map.downstairs_location
            if self.current_floor < floor
            else self.engine.game_map.upstairs_location
        )
        self.current_floor = floor
        self.engine.player.place(
            stairs[0],
            stairs[1],
            self.engine.game_map,
        )

    def descend(self) -> None:
        self.engine.game_world.load_floor(self.engine.game_world.current_floor - 1)

        self.engine.message_log.add_message("You descend the staircase.", color.ascend)

    def ascend(self) -> None:
        next_floor = self.engine.game_world.current_floor + 1
        if len(self.engine.game_world.floors) < next_floor:
            # Load a prefab map if there is one
            if world_prefabs.get(next_floor):
                if self.engine.debug_mode:
                    print(f"Loading prefab map {world_prefabs[next_floor]}")

                self.engine.game_world.load_prefab_map(world_prefabs[next_floor])
                self.engine.game_world.current_floor += 1

                # Get the downstairs location to place the player
                stairs = self.engine.game_map.downstairs_location

                self.engine.player.place(
                    stairs[0],
                    stairs[1],
                    self.engine.game_map,
                )
            else:
                # If we're on the last existing floor, and there's no prefab map, we generate a new one.
                self.engine.game_world.current_floor += 1
                self.engine.game_world.generate_floor()
        else:
            self.engine.game_world.load_floor(next_floor)

        self.engine.message_log.add_message("You ascend the staircase.", color.ascend)
