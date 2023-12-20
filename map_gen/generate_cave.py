"""Generator of cave type maps."""
from __future__ import annotations
from typing import List, TYPE_CHECKING
import random
from map_gen.cave_room import CaveLikeRoom
from map_gen.procgen import (
    get_entities_at_random,
    get_max_value_for_floor,
    tunnel_between,
)
import parameters


from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


def place_entities(room, dungeon, floor):
    """
    Place entities in a given room of a cave.
    """
    max_monsters = get_max_value_for_floor(parameters.max_monsters_by_floor, floor)
    max_items = get_max_value_for_floor(parameters.max_items_by_floor, floor)

    num_monsters = random.randint(0, max_monsters)
    num_items = random.randint(0, max_items)

    monsters = get_entities_at_random(parameters.enemy_chances, num_monsters, floor)
    items = get_entities_at_random(parameters.item_chances, num_items, floor)

    for entity in monsters + items:
        placed = False
        while not placed:
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)

            if dungeon.tiles[x, y]["walkable"] and not any(
                e.x == x and e.y == y for e in dungeon.entities
            ):
                entity.spawn(dungeon, x, y)
                placed = True


def generate_cave(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    engine: Engine,
) -> GameMap:
    """Generate a new dungeon map."""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[CaveLikeRoom] = []

    for _r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        # "RectangularRoom" class makes rectangles easier to work with
        new_room = CaveLikeRoom(
            x, y, room_width, room_height, fill_probability=0.55, generations=4
        )

        # Run through the other rooms and see if they intersect with this one.
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue  # This room intersects, so go to the next attempt.
        # If there are no intersections then the room is valid.

        # Dig out this rooms inner area.

        for h in range(new_room.height):
            for w in range(new_room.width):
                if new_room.inner[h][w] == 1:  # If the cell is filled
                    # Map the local room coordinates to the GameMap coordinates
                    game_map_x = new_room.x1 + w
                    game_map_y = new_room.y1 + h

                    # Check bounds and place the tile if it's within the GameMap
                    if dungeon.in_bounds(game_map_x, game_map_y):
                        dungeon.tiles[game_map_x, game_map_y] = tile_types.floor

        if len(rooms) == 0:
            # The first room, where the player starts.
            player.place(*new_room.center, dungeon)
        else:  # All rooms after the first.
            # Dig out a tunnel between this room and the previous one.
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor

        place_entities(new_room, dungeon, engine.game_world.current_floor)

        rooms.append(new_room)

    # Place stairs going down to the previous level, unless this is the first level.

    if engine.game_world.current_floor > 1:
        dungeon.tiles[rooms[0].center] = tile_types.down_stairs
        dungeon.downstairs_location = rooms[0].center

    dungeon.tiles[rooms[-1].center] = tile_types.up_stairs
    dungeon.upstairs_location = rooms[-1].center

    return dungeon
