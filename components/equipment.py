from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import EquipmentType
from utils import triangular_dist

if TYPE_CHECKING:
    from entity import Actor, Item
    from components.equippable import Ammo


class Equipment(BaseComponent):
    """Component that holds the current Actors equipment."""

    parent: Actor

    def __init__(
        self,
        weapon: Optional[Item] = None,
        armor: Optional[Item] = None,
        ranged: Optional[Item] = None,
        ammo: Optional[Item] = None,
    ):
        self.weapon = weapon
        self.ranged = ranged
        self.armor = armor
        self.ammo = ammo

    @property
    def get_ammo_equippable(self) -> Optional[Ammo]:
        """Get the equippable ammo."""
        if self.ammo is not None and self.ammo.equippable is not None:
            return self.ammo.equippable

        return None

    @property
    def defense_bonus(self) -> int:
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.defense_bonus

        if self.ranged is not None and self.ranged.equippable is not None:
            bonus += self.ranged.equippable.defense_bonus

        if self.armor is not None and self.armor.equippable is not None:
            bonus += self.armor.equippable.defense_bonus

        return bonus

    @property
    def melee_damage(self) -> int:
        damage = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            damage += triangular_dist(*self.weapon.equippable.damage)

        return damage

    @property
    def ranged_damage(self) -> int:
        damage = 0

        if self.ranged is not None and self.ranged.equippable is not None:
            damage += triangular_dist(*self.ranged.equippable.damage)

        return damage

    @property
    def power_bonus(self) -> int:
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.power_bonus

        if self.ranged is not None and self.ranged.equippable is not None:
            bonus += self.ranged.equippable.power_bonus

        if self.armor is not None and self.armor.equippable is not None:
            bonus += self.armor.equippable.power_bonus

        return bonus

    @property
    def ranged_bonus(self) -> int:
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.ranged_bonus

        if self.ranged is not None and self.ranged.equippable is not None:
            bonus += self.ranged.equippable.ranged_bonus

        if self.armor is not None and self.armor.equippable is not None:
            bonus += self.armor.equippable.ranged_bonus

        return bonus

    @property
    def accuracy_bonus(self) -> int:
        bonus = 0

        if self.weapon is not None and self.weapon.equippable is not None:
            bonus += self.weapon.equippable.accuracy_bonus

        if self.ranged is not None and self.ranged.equippable is not None:
            bonus += self.ranged.equippable.accuracy_bonus

        if self.armor is not None and self.armor.equippable is not None:
            bonus += self.armor.equippable.accuracy_bonus

        return bonus

    @property
    def has_ammo(self) -> bool:
        return self.ammo and self.ammo.equippable.amount > 0

    @property
    def has_matching_ammo(self) -> bool:
        return (
            self.ammo
            and self.ammo.equippable.ammo_type == self.ranged.equippable.ammo_type
        )

    def item_is_equipped(self, item: Item) -> bool:
        return item in (self.weapon, self.armor, self.ranged, self.ammo)

    def unequip_message(self, item_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            f"You remove the {item_name}."
        )

    def equip_message(self, item_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            f"You equip the {item_name}."
        )

    def equip_to_slot(self, slot: str, item: Item, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if current_item is not None:
            self.unequip_from_slot(slot, add_message)

        setattr(self, slot, item)

        if add_message:
            self.equip_message(item.name)

    def unequip_from_slot(self, slot: str, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if add_message:
            self.unequip_message(current_item.name)

        setattr(self, slot, None)

    def toggle_equip(self, equippable_item: Item, add_message: bool = True) -> None:
        equipment_type = (
            equippable_item.equippable.equipment_type
            if equippable_item.equippable
            else None
        )
        slot = {
            EquipmentType.WEAPON: "weapon",
            EquipmentType.RANGED: "ranged",
            EquipmentType.AMMO: "ammo",
        }.get(equipment_type, "armor")

        if getattr(self, slot) == equippable_item:
            self.unequip_from_slot(slot, add_message)
        else:
            self.equip_to_slot(slot, equippable_item, add_message)
