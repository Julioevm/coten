"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy
import lzma
import pickle
import traceback
from typing import Optional

import tcod
from tcod import libtcodpy

import color
from engine import Engine
import actor_factories
from event_handlers.base_event_handler import BaseEventHandler
from event_handlers.main_game_event_handler import MainGameEventHandler
from event_handlers.pop_up_message_event_handler import PopupMessage
import item_factories
from game_world import GameWorld

import global_vars


# Load the background image and remove the alpha channel.
background_image = tcod.image.load("menu_background.png")[:, :, :3]


def new_game() -> Engine:
    """Return a brand new game session as an Engine instance."""
    map_width = 80
    map_height = 43

    player = copy.deepcopy(actor_factories.player)

    engine = Engine(player=player, debug_mode=global_vars.DEBUG_MODE)

    engine.game_world = GameWorld(
        engine=engine,
        map_width=map_width,
        map_height=map_height,
    )

    if global_vars.DEBUG_MODE:
        engine.game_world.load_prefab_map("debug_room")
        engine.message_log.add_message(
            "DEBUG MODE ENABLED",
            color.yellow,
        )
    else:
        engine.game_world.generate_floor()

    engine.update_fov()

    engine.message_log.add_message(
        "As you step into the darkness, a malevolent laughter echoes from the castle!",
        color.welcome_text,
    )

    dagger = copy.deepcopy(item_factories.dagger)
    dagger.parent = player.inventory

    player.inventory.items.append(dagger)
    player.equipment.toggle_equip(dagger, add_message=False)

    return engine


def load_game(filename: str) -> Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


class MainMenu(BaseEventHandler):
    """Handle the main menu rendering and input."""

    def on_render(self, console: tcod.console.Console) -> None:
        """Render the main menu on a background image."""
        # Make the image fill in the console size with the background image
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "Castle of the Eternal Night",
            fg=color.menu_title,
            alignment=libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By Julio Valls",
            fg=color.menu_title,
            alignment=libtcodpy.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(
            ["[N] Play a new game", "[C] Continue last game", "[Q] Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.menu_text,
                bg=color.black,
                alignment=libtcodpy.CENTER,
                bg_blend=libtcodpy.BKGND_ALPHA(64),
            )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[BaseEventHandler]:
        if event.sym in (tcod.event.KeySym.q, tcod.event.KeySym.ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.KeySym.c:
            try:
                return MainGameEventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return PopupMessage(self, "No saved game to load.")
            except Exception as exc:
                traceback.print_exc()  # Print to stderr.
                return PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.KeySym.n:
            return MainGameEventHandler(new_game())

        return None
