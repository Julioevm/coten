from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from tcod.console import Console
from tcod.map import compute_fov

import exceptions
from message_log import MessageLog
import render_functions

import lzma
import pickle

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap
    from game_world import GameWorld


class Engine:
    game_map: GameMap
    game_world: GameWorld

    def __init__(self, player: Actor):
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player
        self.current_turn = 0
        self.scheduled_effects = []

    def tick(self) -> None:
        """Increase the turn counter"""
        self.current_turn += 1

    def handle_enemy_turns(self) -> None:
        """Iterate over all enemies, and for each one, call the enemy.ai.perform() method."""
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass  # Ignore impossible action exceptions from AI.

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
        )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        self.game_map.render(console)

        self.message_log.render(console=console, x=21, y=45, width=40, height=5)

        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )

        render_functions.render_dungeon_level(
            console=console,
            dungeon_level=self.game_world.current_floor,
            location=(0, 47),
        )

        render_functions.render_names_at_mouse_location(
            console=console, x=21, y=44, engine=self
        )

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)

    def schedule_effect(self, delay: int, effect: Callable) -> None:
        """Schedule an effect to be called after a certain number of turns."""
        scheduled_turn = self.current_turn + delay
        self.scheduled_effects.append((scheduled_turn, effect))

    def process_scheduled_effects(self) -> None:
        """Process and apply any effects that are scheduled for this turn."""

        for turn, effect in self.scheduled_effects:
            if turn == self.current_turn:
                effect()  # Call the scheduled effect

        # Remove effects that have been executed this turn
        self.scheduled_effects = [
            (turn, effect)
            for turn, effect in self.scheduled_effects
            if turn > self.current_turn
        ]
