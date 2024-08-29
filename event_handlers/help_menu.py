from __future__ import annotations
from typing import Optional
import tcod
from tcod import libtcodpy
import color
from engine import Engine
from event_handlers import keys
from event_handlers.event_handler import EventHandler
from event_handlers.main_game_event_handler import MainGameEventHandler


class HelpMenu(EventHandler):
    """Display the help menu."""

    help_text = (
        "Castle of The Eternal Night is a classic rogue-like built with Python.",
        "You are a vampire hunter that sets to put an end to the",
        "evil vampire lord terrorizing these lands.",
        "To that end you enter the twisted castle with the goal of reaching",
        "the top defeating the wicked creature.",
        "",
        "To use, equip or unequip items, check your (I)nventory.",
        "",
        "Controls:",
        "Arrows, VIM keys and numpad for movement.",
        ". Wait turn",
        "c Character sheet",
        "I Inventory",
        "G Grab item from the ground",
        "D Drop",
        "Q Quick quaff a health potion",
        "V Message log",
        "F fire ranged weapon. Equip both the weapon and the right ammo!",
        "/ To look around and inspect the map. You can use the mouse as well.",
        "< or > Go up or down stairs.",
        "SPACE - Use equipped weapon's special ability",
    )

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def print_help_text(self, console: tcod.console.Console) -> None:
        y = 2
        for text in self.help_text:
            console.print(x=2, y=y, string=text, fg=color.white)
            y += 1

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)  # Draw the main state as the background.

        help_console = tcod.console.Console(console.width - 6, console.height - 6)

        # Draw a frame with a custom banner title.
        help_console.draw_frame(0, 0, help_console.width, help_console.height)
        help_console.print_box(
            0, 0, help_console.width, 1, "┤Help├", alignment=libtcodpy.CENTER
        )

        self.print_help_text(help_console)
        help_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        # Fancy conditional movement to make it feel right.
        if event.sym in keys.CURSOR_Y_KEYS:
            adjust = keys.CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.KeySym.HOME:
            self.cursor = 0  # Move directly to the top message.
        elif event.sym == tcod.event.KeySym.END:
            self.cursor = self.log_length - 1  # Move directly to the last message.
        else:  # Any other key moves back to the main game state.
            return MainGameEventHandler(self.engine)
        return None
