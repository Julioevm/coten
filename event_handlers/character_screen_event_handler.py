import tcod
import color
from event_handlers.ask_user_event_handler import AskUserEventHandler


class CharacterScreenEventHandler(AskUserEventHandler):
    TITLE = "Character Information"

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)
        player = self.engine.player
        if player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=10,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(x=x + 1, y=y + 1, string=f"Level: {player.level.current_level}")
        console.print(x=x + 1, y=y + 2, string=f"XP: {player.level.current_xp}")
        console.print(
            x=x + 1,
            y=y + 3,
            string=f"XP for next Level: {player.level.experience_to_next_level}",
        )

        power_string = (
            f"Power: {player.fighter.base_power} + ({player.equipment.power_bonus})"
        )

        if player.fighter.power_boost > 0:
            power_string += f" + {player.fighter.power_boost}"
        console.print(
            x=x + 1,
            y=y + 4,
            string=power_string,
            fg=color.power_boost if player.fighter.power_boost > 0 else None,
        )
        
        # Add weapon damage

        console.print(
            x=x + 1,
            y=y + 5,
            string=f"Ranged: ({player.equipment.ranged_bonus})",
        )

        # the defense value displayed is only the 10% of the actual value, rounded

        defense_string = f"Defense: {round(player.fighter.base_defense * 0.1)} + ({round(player.equipment.defense_bonus * 0.1)})"
        if player.fighter.defense_boost > 0:
            defense_string += f" + {round(player.fighter.defense_boost * 0.1)}"

        console.print(
            x=x + 1,
            y=y + 6,
            string=defense_string,
            fg=color.defense_boost if player.fighter.defense_boost > 1 else None,
        )

        console.print(x=x + 1, y=y + 7, string=f"Turns: {self.engine.current_turn}")
