"""Rendering utility functions."""
from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from tcod.console import Console
    from engine import Engine
    from game_map import GameMap


def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = ", ".join(
        entity.name for entity in game_map.entities if entity.x == x and entity.y == y
    )

    return names.capitalize()


def render_bar(
    console: Console,
    current_value: int,
    maximum_value: int,
    total_width: int,
    bar_color,
    empty_bar_color,
    text_color,
    x: int,
    y: int,
    label: str = "",
) -> None:
    """
    Renders a progress bar on the console.

        Parameters:
        console (Console): The console object where the bar will be rendered.
        current_value (int): The current value represented by the bar.
        maximum_value (int): The maximum value the bar can represent.
        total_width (int): The total width of the bar in characters.
        bar_color: The color of the filled portion of the bar.
        empty_bar_color: The color of the empty portion of the bar.
        text_color: The color of the text that will be displayed.
        x (int): The x-coordinate on the console where the bar starts.
        y (int): The y-coordinate on the console where the bar starts.
        label (str, optional): A label displayed before the bar values. Defaults to an empty string.
    """
    bar_width = int(float(current_value) / maximum_value * total_width)

    # Draw the background (empty bar)
    console.draw_rect(x=x, y=y, width=total_width, height=1, ch=1, bg=empty_bar_color)

    # Draw the bar on top
    if bar_width > 0:
        console.draw_rect(x=x, y=y, width=bar_width, height=1, ch=1, bg=bar_color)

    # Print the text with the values
    console.print(
        x=x + 1, y=y, string=f"{label}: {current_value}/{maximum_value}", fg=text_color
    )


def render_dungeon_level(
    console: Console, name: str, dungeon_level: int, location: Tuple[int, int]
) -> None:
    """
    Render the level the player is currently on, at the given location.
    """
    x, y = location

    console.print(x=x, y=y, string=f"{name} floor: {dungeon_level}")


def render_potions(console: Console, location: Tuple[int, int], potions: int) -> None:
    x, y = location
    console.print(x=x, y=y, string=f"Potions: {potions}")


def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = get_names_at_location(
        x=mouse_x, y=mouse_y, game_map=engine.game_map
    )

    console.print(x=x, y=y, string=names_at_mouse_location)
