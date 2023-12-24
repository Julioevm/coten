from __future__ import annotations

from typing import List, TYPE_CHECKING

from components import consumable
from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item


class Inventory(BaseComponent):
    """Hold a list of items and sets a max capacity."""

    parent: Actor

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[Item] = []

    @property
    def healing_items(self) -> List[Item]:
        """Returns s list of healing items in the inventory."""
        return [
            item
            for item in self.items
            if item.consumable
            and isinstance(item.consumable, consumable.HealingConsumable)
        ]

    def drop(self, item: Item) -> None:
        """
        Removes an item from the inventory and restores it to the game map, at the player's current location.
        """
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.gamemap)

        self.engine.message_log.add_message(f"You dropped the {item.name}.")
