from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import AmmoType, EquipmentType

if TYPE_CHECKING:
    from entity import Item


class Equippable(BaseComponent):
    parent: Item

    def __init__(
        self,
        equipment_type: EquipmentType,
        power_bonus: int = 0,
        ranged_bonus: int = 0,
        defense_bonus: int = 0,
    ):
        self.equipment_type = equipment_type

        self.power_bonus = power_bonus
        self.ranged_bonus = ranged_bonus
        self.defense_bonus = defense_bonus


class Ranged(Equippable):
    def __init__(self, ammo_type: AmmoType, ranged_bonus: int) -> None:
        self.ammo_type = ammo_type
        super().__init__(equipment_type=EquipmentType.RANGED, ranged_bonus=ranged_bonus)


class Ammo(Equippable):
    parent: Item

    def __init__(self, ammo_type: AmmoType, amount: int):
        self.ammo_type = ammo_type
        self.amount = amount
        super().__init__(equipment_type=EquipmentType.AMMO)


class Dagger(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=2)


class Axe(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=3)


class Sword(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=4)


class Bow(Ranged):
    def __init__(self) -> None:
        super().__init__(
            ammo_type=AmmoType.ARROW,
            ranged_bonus=3,
        )


class Arrows(Ammo):
    def __init__(self) -> None:
        super().__init__(ammo_type=AmmoType.ARROW, amount=20)


class Bolts(Ammo):
    def __init__(self) -> None:
        super().__init__(ammo_type=AmmoType.BOLT, amount=15)


class LeatherArmor(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=1)


class ChainMail(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=3)


class PlateArmor(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=5)
