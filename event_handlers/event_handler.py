from __future__ import annotations


from typing import Optional

import tcod.event
from actions import Action

import color
from engine import Engine
from event_handlers.base_event_handler import BaseEventHandler
import exceptions


class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine."""
        from event_handlers.main_game_event_handler import MainGameEventHandler
        from event_handlers.game_over_event_handler import GameOverEventHandler
        from event_handlers.level_up_event_handler import LevelUpEventHandler

        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            # A valid action was performed.
            if not self.engine.player.is_alive:
                # The player was killed sometime during or after the action.
                return GameOverEventHandler(self.engine)
            if self.engine.player.level.requires_level_up:
                return LevelUpEventHandler(self.engine)

            return MainGameEventHandler(self.engine)  # Return to the main handler.
        return self

    def handle_action(self, action: Optional[Action]) -> bool:
        """Handle actions returned from event methods.

        Returns True if the action will advance a turn.
        """
        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False  # Skip enemy turn on exceptions.

        self.engine.handle_enemy_turns()

        self.engine.process_scheduled_effects()

        self.engine.update_fov()

        self.engine.tick()
        return True

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def on_render(self, console: tcod.console.Console) -> None:
        self.engine.render(console)
