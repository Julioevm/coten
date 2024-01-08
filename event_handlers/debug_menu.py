from typing import Optional
import tcod
from actions import SpawnEnemiesAction
import actor_factories
from event_handlers.ask_user_event_handler import AskUserEventHandler

from event_handlers.base_event_handler import ActionOrHandler


class DebugMenuEventHandler(AskUserEventHandler):
    TITLE = "Debug Menu"
    debug_options = [
        "Reveal Map",
        "Heal Player",
        "Spawn bats",
        # Add more debug options here
    ]

    def on_render(self, console: tcod.console.Console) -> None:
        """Render the debug menu, which displays the options for debugging."""
        super().on_render(console)

        height = len(self.debug_options) + 2
        width = max(len(option) for option in self.debug_options) + 6

        x = console.width // 2 - width // 2
        y = console.height // 2 - height // 2

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        for i, option in enumerate(self.debug_options):
            option_key = chr(ord("a") + i)
            option_string = f"({option_key}) {option}"
            console.print(x + 1, y + i + 1, option_string)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= len(self.debug_options) - 1:
            if index == 0:  # Reveal Map option
                return self.reveal_map()
            if index == 1:  # Heal Player option
                self.heal()
            if index == 2:
                self.spawn_bats()
            # Add more index checks here if you add more debug options
        return super().ev_keydown(event)

    def reveal_map(self) -> Optional[ActionOrHandler]:
        """Reveals the entire map."""
        self.engine.game_map.reveal_map()
        return None

    def heal(self) -> None:
        """Heals the player to full health."""
        self.engine.player.fighter.heal(self.engine.player.fighter.max_hp)

    def spawn_bats(self) -> None:
        player = self.engine.player
        SpawnEnemiesAction(player, actor_factories.bat, 3, 3).perform()
