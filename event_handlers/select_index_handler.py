from typing import Callable, Optional, Tuple

import tcod
from actions import Action
from engine import Engine
from event_handlers import keys
from event_handlers.ask_user_event_handler import AskUserEventHandler
from event_handlers.base_event_handler import ActionOrHandler
from event_handlers.main_game_event_handler import MainGameEventHandler
import color


class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""

    def __init__(self, engine: Engine):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.console.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.rgb["bg"][x, y] = color.white
        console.rgb["fg"][x, y] = color.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """Check for key movement or confirmation keys."""
        key = event.sym
        if key in keys.MOVE_KEYS:
            modifier = 1  # Holding modifier keys will speed up key movement.
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = keys.MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            # Clamp the cursor index to the map size.
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))
            self.engine.mouse_location = x, y
            return None

        if key in keys.CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)

        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """Left click confirms a selection."""
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        """Called when an index is selected."""
        raise NotImplementedError()


class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard."""

    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        """Return to main handler."""
        return MainGameEventHandler(self.engine)


class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a single enemy. Only the enemy selected will be affected."""

    def __init__(
        self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__(engine)

        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""

    def __init__(
        self,
        engine: Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.console.Console) -> None:
        """Highlight the tile under the cursor and the tiles within the radius."""
        super().on_render(console)

        x, y = self.engine.mouse_location

        # Get the range of tiles to highlight
        start_x = x - self.radius
        start_y = y - self.radius
        end_x = x + self.radius + 1
        end_y = y + self.radius + 1

        # Highlight the individual tiles within the radius
        for tile_x in range(start_x, end_x):
            for tile_y in range(start_y, end_y):
                # Check if the tile is within the circular radius
                if (tile_x - x) ** 2 + (tile_y - y) ** 2 <= self.radius**2:
                    console.rgb["bg"][tile_x, tile_y] = color.red

        # Mark the center tile with a special character or color
        center_mark_char = "+"  # Choose a character that stands out
        center_mark_color = color.yellow  # Choose a bright color for the center mark
        console.print(x, y, center_mark_char, fg=center_mark_color)

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))
