#!/usr/bin/env python3
import sys
import traceback
import tcod

import color
from event_handlers.base_event_handler import BaseEventHandler
from event_handlers.event_handler import EventHandler
import exceptions

import setup_game
import global_vars


def save_game(handler: BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active Engine then save it."""
    if isinstance(handler, EventHandler):
        handler.engine.save_as(filename)
        print("Game saved.")


def main() -> None:
    """Main startup function."""
    screen_width = 80
    screen_height = 50

    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    handler: BaseEventHandler = setup_game.MainMenu()

    # Check if '-debug' is present in sys.argv
    debug_mode = "-debug" in sys.argv

    global_vars.DEBUG_MODE = debug_mode
    title = (
        "Castle of the eternal Night - DEBUG MODE"
        if debug_mode
        else "Castle of the eternal Night"
    )

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title=title,
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(screen_width, screen_height, order="F")
        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(root_console)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()  # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # Save and quit.
            save_game(handler, "savegame.sav")
            raise
        except BaseException:  # Save on any other unexpected exception.
            save_game(handler, "savegame.sav")
            raise


if __name__ == "__main__":
    main()
