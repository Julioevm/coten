from __future__ import annotations
from typing import Optional, TYPE_CHECKING


import tile_types
import tcod.event
import color
import actions
from actions import (
    Action,
    BumpAction,
    MoveToTileAction,
    PickupAction,
    QuickHealAction,
    SpecialAbilityAction,
    WaitAction,
    RangedAttackAction,
)
from event_handlers import keys
from event_handlers.character_screen_event_handler import CharacterScreenEventHandler
from event_handlers.debug_menu import DebugMenuEventHandler
from event_handlers.event_handler import EventHandler


if TYPE_CHECKING:
    from event_handlers.base_event_handler import ActionOrHandler


class MainGameEventHandler(EventHandler):
    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        action: Optional[Action] = None
        """Handle the player clicking on the map."""
        game_map = self.engine.game_map

        if (
            self.engine.game_map.in_bounds(event.tile.x, event.tile.y)
            and game_map.explored[event.tile.x, event.tile.y]
        ):
            if (
                game_map.tiles["walkable"][event.tile.x, event.tile.y]
                or game_map.tiles[event.tile.x, event.tile.y] in tile_types.door_tiles
            ):
                return MoveToTileAction(self.engine.player, event.tile.x, event.tile.y)

        return action

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        from event_handlers.select_index_handler import SingleRangedAttackHandler
        from event_handlers.history_viewer import HistoryViewer
        from event_handlers.inventory_event_handler import (
            InventoryActivateHandler,
            InventoryDropHandler,
        )
        from event_handlers.select_index_handler import LookHandler
        from event_handlers.help_menu import HelpMenu

        action: Optional[Action] = None
        key = event.sym
        modifier = event.mod

        player = self.engine.player
        is_debug_mode = self.engine.debug_mode

        if (
            key == tcod.event.KeySym.COMMA or key == tcod.event.KeySym.PERIOD
        ) and modifier & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
            return actions.TakeStairsAction(player)

        if key in keys.MOVE_KEYS:
            dx, dy = keys.MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in keys.WAIT_KEYS:
            action = WaitAction(player)

        elif key == tcod.event.KeySym.ESCAPE:
            raise SystemExit()

        elif key == tcod.event.KeySym.v:
            return HistoryViewer(self.engine)

        elif key == tcod.event.KeySym.g:
            action = PickupAction(player)

        elif key == tcod.event.KeySym.i:
            return InventoryActivateHandler(self.engine)

        elif key == tcod.event.KeySym.f:
            if not self.engine.player.equipment.ranged:
                self.engine.message_log.add_message(
                    "You have no ranged weapon equipped.", color.invalid
                )
                return action
            if (
                not self.engine.player.equipment.has_ammo
                or not self.engine.player.equipment.has_matching_ammo
            ):
                self.engine.message_log.add_message(
                    "You have no right ammo equipped.", color.invalid
                )
                return action
            return SingleRangedAttackHandler(
                self.engine, callback=lambda xy: RangedAttackAction(player, xy)
            )

        elif key == tcod.event.KeySym.d:
            return InventoryDropHandler(self.engine)

        elif key == tcod.event.KeySym.c:
            return CharacterScreenEventHandler(self.engine)

        elif key == tcod.event.KeySym.q:
            action = QuickHealAction(player)

        elif key == tcod.event.KeySym.SLASH:
            return LookHandler(self.engine)

        elif key == tcod.event.KeySym.QUOTE and is_debug_mode:
            return DebugMenuEventHandler(self.engine)

        elif key == tcod.event.KeySym.F1:
            return HelpMenu(self.engine)

        elif key == tcod.event.KeySym.SPACE:
            return SpecialAbilityAction(player)

        # No valid key was pressed
        return action
