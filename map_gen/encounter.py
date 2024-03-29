from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from entity import Entity, Actor
    from entity import Item
    from map_gen.base_room import Room


class Encounter:
    def __init__(
        self,
        enemies: List[Actor],
        items: List[Item] = [],
        decorations: List[Entity] = [],
        min_room_size=9,
    ):
        self.enemies = enemies
        self.items = items
        self.decorations = decorations
        self.min_room_size = min_room_size

    def is_room_suitable(self, room: Room) -> bool:
        return room.size >= self.min_room_size
