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

        if player.fighter.power_boost > 1:
            console.print(
                x=x + 1,
                y=y + 4,
                string=f"Attack: {player.fighter.base_power} + ({player.equipment.power_bonus}) + {player.fighter.power_boost}",
                fg=color.power_boost,
            )
        else:
            console.print(
                x=x + 1,
                y=y + 4,
                string=f"Attack: {player.fighter.base_power} + ({player.equipment.power_bonus})",
            )
        console.print(
            x=x + 1,
            y=y + 5,
            string=f"Ranged: ({player.equipment.ranged.equippable.power_bonus})",
        )
        if player.fighter.defense_boost > 1:
            console.print(
                x=x + 1,
                y=y + 6,
                string=f"Defense: {player.fighter.base_defense} + ({player.equipment.defense_bonus}) + {player.fighter.defense_boost}",
                fg=color.defense_boost,
            )
        else:
            console.print(
                x=x + 1,
                y=y + 7,
                string=f"Defense: {player.fighter.base_defense} + ({player.equipment.defense_bonus})",
            )

        console.print(x=x + 1, y=y + 7, string=f"Turns: {self.engine.current_turn}")
