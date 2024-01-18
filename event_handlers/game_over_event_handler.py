from __future__ import annotations

import os

from typing import Optional

import tcod.event
from tcod import libtcodpy

import color
from event_handlers.event_handler import EventHandler
from event_handlers.main_game_event_handler import MainGameEventHandler
import exceptions


class GameOverEventHandler(EventHandler):
    """Event handler for the game over screen."""

    def on_render(self, console: tcod.console.Console) -> None:
        console.rgb["bg"] = color.black
        console.rgb["fg"] = color.red
        console.print(
            console.width // 2,
            console.height // 2,
            "YOU DIED!",
            fg=color.red,
            alignment=libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height // 2 + 3,
            "Press Enter to restart",
            fg=color.red,
            alignment=libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height // 2 + 4,
            "Press Esc to exit",
            fg=color.red,
            alignment=libtcodpy.CENTER,
        )

    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")  # Deletes the active save file.
        raise exceptions.QuitWithoutSaving()  # Avoid saving a finished game.

    def on_restart(self) -> MainGameEventHandler:
        """Handle restarting the game."""
        from setup_game import new_game  # pylint: disable=import-outside-toplevel

        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")  # Deletes the active save file.

        return MainGameEventHandler(new_game())

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        if event.sym == tcod.event.KeySym.ESCAPE:
            self.on_quit()
        elif (
            event.sym == tcod.event.KeySym.KP_ENTER
            or event.sym == tcod.event.KeySym.RETURN
        ):
            return self.on_restart()


class VictoryEventHandler(EventHandler):
    """Event handler for the game over screen."""

    def on_render(self, console: tcod.console.Console) -> None:
        console.rgb["bg"] = color.black
        console.rgb["fg"] = color.red
        console.print(
            console.width // 2,
            console.height // 2,
            "Congratulations!",
            fg=color.yellow,
            alignment=libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height // 2 + 1,
            "You defeated the evil in the castle!",
            fg=color.yellow,
            alignment=libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height // 2 + 3,
            f"Turns: {self.engine.current_turn} Total Exp: {self.engine.player.level.total_xp}",
            fg=color.red,
            alignment=libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height // 2 + 5,
            "Press Enter to start a new game",
            fg=color.red,
            alignment=libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height // 2 + 6,
            "Press Esc to exit",
            fg=color.red,
            alignment=libtcodpy.CENTER,
        )

    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")  # Deletes the active save file.
        raise exceptions.QuitWithoutSaving()  # Avoid saving a finished game.

    def on_restart(self) -> MainGameEventHandler:
        """Handle restarting the game."""
        from setup_game import new_game  # pylint: disable=import-outside-toplevel

        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")  # Deletes the active save file.

        return MainGameEventHandler(new_game())

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        if event.sym == tcod.event.KeySym.ESCAPE:
            self.on_quit()
        elif (
            event.sym == tcod.event.KeySym.KP_ENTER
            or event.sym == tcod.event.KeySym.RETURN
        ):
            return self.on_restart()
