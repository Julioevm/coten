from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from tcod.console import Console
from tcod.map import compute_fov

import exceptions
from message_log import MessageLog
import render_functions
import color

import lzma
import pickle

from turn_manager import TurnManager

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap
    from game_world import GameWorld


class Engine:
    game_map: GameMap
    game_world: GameWorld
    turn_manager: TurnManager

    def __init__(self, player: Actor, debug_mode=False):
        self.debug_mode = debug_mode
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player
        self.current_turn = 0
        self.scheduled_effects = []

    def tick(self) -> None:
        """Increase the turn counter"""
        self.current_turn += 1

    def handle_entity_turns(self) -> None:
        """Iterate over the entities and handle their actions."""

        # Handle player turn first
        player = self.player

        try:
            # If the player is under a special AI behaviour ignore the user action
            action = player.ai.get_action() if player.ai else player.fighter.next_action
            action.perform()
            action.exhaust_energy()
        except exceptions.Impossible as exc:
            # If the action results in an impossible error, we want to retry the turn.
            self.message_log.add_message(exc.args[0], color.impossible)
            return

        player.status.process_active_effects()

        # Since the player gets the act first, when he comsumes more energy than the the other actors
        # we should give a bonus to the other actos, to simulate having more time to act.
        # We could substract the entity.speed from the energy used by the player to get the excess energy and add it to the entity.
        # E.g. player uses an action of 150 energy. The entity has speed of 100: 150 - 100 = 50 extra energy to add to it.
        # All actions cost 100 for now so theres no difference at the moment.
        for entity in set(self.game_map.actors):
            entity.fighter.regain_energy()

        for entity in set(self.game_map.actors) - {player}:
            self.turn_manager.add_actor(entity)

        # Handle other actors

        while self.turn_manager.has_actors:
            entity = self.turn_manager.get_next_actor()

            can_act = True
            while entity and entity.fighter.energy > 0 and can_act:
                can_act = False

                if entity.ai:
                    action = entity.ai.get_action()
                    if action.can_perform:
                        try:
                            can_act = True
                            action.exhaust_energy()
                            action.perform()
                        except exceptions.Impossible:
                            can_act = False

            if entity.status:
                try:
                    entity.status.process_active_effects()
                except exceptions.Impossible:
                    pass  # Ignore impossible status exceptions from AI.

        self.process_scheduled_effects()
        self.tick()

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

        # HP Bar
        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
            bar_color=color.hp_bar_filled,
            empty_bar_color=color.hp_bar_empty,
            text_color=color.hp_bar_text,
            x=0,
            y=45,
            label="HP",
        )

        # XP bar
        render_functions.render_bar(
            console=console,
            current_value=self.player.level.current_xp,
            maximum_value=self.player.level.experience_to_next_level,
            total_width=20,
            x=0,
            y=46,
            bar_color=color.exp_bar_filled,
            empty_bar_color=color.exp_bar_empty,
            text_color=color.exp_bar_text,
            label="EXP",
        )

        render_functions.render_dungeon_level(
            console=console,
            name=self.game_map.name,
            dungeon_level=self.game_world.current_floor,
            location=(0, 47),
        )

        render_functions.render_potions(
            console=console,
            location=(0, 48),
            potions=len(self.player.inventory.healing_items),
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
