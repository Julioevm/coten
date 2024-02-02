from typing import Tuple

import numpy as np  # type: ignore

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", bool),  # True if this tile can be walked over.
        ("transparent", bool),  # True if this tile doesn't block FOV.
        ("dark", graphic_dt),  # Graphics for when this tile is not in FOV.
        ("light", graphic_dt),  # Graphics for when the tile is in FOV.
    ]
)


def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types"""
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)


# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt)

floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(" "), (255, 255, 255), (22, 24, 43)),
    light=(ord(" "), (255, 255, 255), (50, 50, 100)),
)
wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord(" "), (255, 255, 255), (31, 32, 45)),
    light=(ord(" "), (255, 255, 255), (70, 70, 100)),
)
closed_door = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("+"), (255, 255, 255), (31, 32, 45)),
    light=(ord("+"), (255, 255, 255), (70, 70, 100)),
)
open_door = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("-"), (255, 255, 255), (22, 24, 43)),
    light=(ord("-"), (255, 255, 255), (50, 50, 100)),
)
down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), (0, 0, 100), (22, 24, 43)),
    light=(ord(">"), (255, 255, 255), (50, 50, 100)),
)
up_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("<"), (0, 0, 100), (22, 24, 43)),
    light=(ord("<"), (255, 255, 255), (50, 50, 100)),
)
dirt_floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(" "), (255, 255, 255), (93, 82, 32)),
    light=(ord(" "), (255, 255, 255), (200, 180, 50)),
)
cave_wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord(" "), (255, 255, 255), (58, 49, 26)),
    light=(ord(" "), (255, 255, 255), (130, 110, 50)),
)
cave_down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), (0, 0, 100), (93, 82, 32)),
    light=(ord(">"), (255, 255, 255), (200, 180, 50)),
)
cave_up_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("<"), (0, 0, 100), (93, 82, 32)),
    light=(ord("<"), (255, 255, 255), (200, 180, 50)),
)


stair_tiles = [down_stairs, up_stairs, cave_down_stairs, cave_up_stairs]

door_tiles = [closed_door, open_door]
