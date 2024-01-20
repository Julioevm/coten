from __future__ import annotations

from typing import TYPE_CHECKING

import color
from components.base_component import BaseComponent
from render_order import RenderOrder
from utils import triangular_dist

if TYPE_CHECKING:
    from actions import Action
    from entity import Actor


class Fighter(BaseComponent):
    """Actor component that holds the relevant information to handle combat."""

    parent: Actor

    def __init__(
        self,
        hp: int,
        base_defense: int,
        base_power: int,
        base_damage: tuple[int, int] = (0, 2),
        base_accuracy: int = 100,
        base_speed=100,
        bleeds=True,
        on_death: Action | None = None,
    ):
        self.max_hp = hp
        self._hp = hp
        self.base_defense = base_defense
        self.base_power = base_power
        self.base_damage = base_damage
        self.base_accuracy = base_accuracy
        self.energy = 0
        self.power_boost = 0
        self.defense_boost = 0
        self.base_speed = base_speed
        self.bleeds = bleeds

        self.next_action: Action | None = None
        self.on_death = on_death

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0:
            self.die()

    @property
    def defense(self) -> int:
        return self.base_defense + self.defense_bonus + self.defense_boost

    @property
    def melee_damage(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.melee_damage + self.power
        return triangular_dist(*self.base_damage) + self.power

    @property
    def power(self) -> int:
        return self.base_power + self.power_bonus + self.power_boost

    @property
    def accuracy(self) -> int:
        return self.base_accuracy + self.accuracy_bonus

    @property
    def defense_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.defense_bonus
        else:
            return 0

    @property
    def power_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.power_bonus
        else:
            return 0

    @property
    def accuracy_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.accuracy_bonus
        else:
            return 0

    def regain_energy(self):
        self.energy += self.base_speed

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount

        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def take_damage(self, amount: int) -> None:
        self.hp -= amount

    def die(self) -> None:
        if self.engine.player is self.parent:
            death_message = "You died!"
            death_message_color = color.player_die
        else:
            death_message = f"{self.parent.name} is dead!"
            death_message_color = color.enemy_die

        self.parent.char = "%"
        self.parent.color = self.parent.remains_color
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.is_alive = False
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.message_log.add_message(death_message, death_message_color)

        self.engine.player.level.add_xp(self.parent.level.xp_given)

        if self.on_death:
            self.on_death.perform()
