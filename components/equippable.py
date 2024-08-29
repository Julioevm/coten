from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Callable

from components.base_component import BaseComponent
from equipment_types import AmmoType, EquipmentType
from exceptions import Impossible

if TYPE_CHECKING:
    from entity import Item


class Equippable(BaseComponent):
    parent: Item

    def __init__(
        self,
        equipment_type: EquipmentType,
        damage: tuple[int, int] = (0, 0),
        power_bonus: int = 0,
        ranged_bonus: int = 0,
        defense_bonus: int = 0,
        accuracy_bonus: int = 0,
    ):
        self.equipment_type = equipment_type

        self.power_bonus = power_bonus
        self.damage = damage
        self.ranged_bonus = ranged_bonus
        self.defense_bonus = defense_bonus
        self.accuracy_bonus = accuracy_bonus


class Melee(Equippable):
    def __init__(
        self,
        damage: tuple[int, int],
        power_bonus: int = 0,
        special_ability: Optional[Callable] = None
    ) -> None:
        super().__init__(
            equipment_type=EquipmentType.WEAPON,
            power_bonus=power_bonus,
            damage=damage,
        )
        self.special_ability = special_ability


class Ranged(Equippable):
    def __init__(
        self, ammo_type: AmmoType, damage: tuple[int, int], ranged_bonus: int = 0
    ) -> None:
        super().__init__(
            equipment_type=EquipmentType.RANGED,
            ranged_bonus=ranged_bonus,
            damage=damage,
        )
        self.ammo_type = ammo_type


class Ammo(Equippable):
    parent: Item

    def __init__(self, ammo_type: AmmoType, amount: int):
        self.ammo_type = ammo_type
        self.amount = amount
        super().__init__(equipment_type=EquipmentType.AMMO)

    def consume(self) -> None:
        if self.amount == 0:
            raise Impossible("No ammo left!")
        self.amount -= 1


class Dagger(Melee):
    def __init__(self, damage: tuple[int, int]) -> None:
        super().__init__(damage=damage)


class Axe(Melee):
    def __init__(self, damage: tuple[int, int], special_ability: Optional[Callable] = None) -> None:
        super().__init__(damage=damage, special_ability=special_ability)


class Sword(Melee):
    def __init__(self, damage: tuple[int, int], special_ability: Optional[Callable] = None) -> None:
        super().__init__(damage=damage, special_ability=special_ability)


class Spear(Melee):
    def __init__(self, damage: tuple[int, int]) -> None:
        super().__init__(damage=damage)


class Bow(Ranged):
    def __init__(self, ammo_type=AmmoType.ARROW, damage=(1, 3), ranged_bonus=0) -> None:
        super().__init__(ammo_type=ammo_type, ranged_bonus=ranged_bonus, damage=damage)


class Arrows(Ammo):
    def __init__(self, ammo_type=AmmoType.ARROW, amount=15) -> None:
        super().__init__(ammo_type=ammo_type, amount=amount)


class LeatherArmor(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=10)


class ChainMail(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=20)


class PlateArmor(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=30)
