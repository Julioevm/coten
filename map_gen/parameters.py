"""Parameters for different settings of the dungeon generation."""
from __future__ import annotations
from typing import Dict, List, Tuple, TYPE_CHECKING
import actor_factories
import item_factories

if TYPE_CHECKING:
    from entity import Entity

max_items_by_floor = [
    (1, 1),
    (4, 2),
]

max_monsters_by_floor = [
    (1, 1),
    (2, 2),
    (4, 3),
    (6, 5),
]

item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [
        (item_factories.health_potion, 30),
        (item_factories.defense_boost_potion, 5),
        (item_factories.power_boost_potion, 5),
        (item_factories.holy_water_vial, 5),
    ],
    2: [
        (item_factories.bow, 15),
        (item_factories.arrows, 20),
        (item_factories.confusion_scroll, 10),
        (item_factories.leather_armor, 15),
        (item_factories.defense_boost_potion, 10),
        (item_factories.power_boost_potion, 10),
    ],
    3: [
        (item_factories.fireball_scroll, 5),
        (item_factories.chain_mail, 5),
        (item_factories.axe, 5),
        (item_factories.holy_water_vial, 15),
    ],
    4: [
        (item_factories.lightning_scroll, 10),
        (item_factories.sword, 5),
        (item_factories.great_health_potion, 15),
    ],
    5: [
        (item_factories.fireball_scroll, 10),
        (item_factories.plate_armor, 5),
        (item_factories.leather_armor, 5),
    ],
    6: [(item_factories.fireball_scroll, 25), (item_factories.chain_mail, 15)],
}

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [
        (actor_factories.zombie, 80),
        (actor_factories.hound, 10),
        (actor_factories.bat, 20),
    ],
    1: [(actor_factories.skeleton_archer, 20)],
    2: [
        (actor_factories.bat, 5),
    ],
    3: [
        (actor_factories.ghoul, 15),
        (actor_factories.brute_zombie, 15),
        (actor_factories.hound, 15),
    ],
    4: [(actor_factories.seducer, 15)],
    5: [
        (actor_factories.zombie, 30),
        (actor_factories.ghoul, 30),
        (actor_factories.brute_zombie, 30),
        (actor_factories.hound, 5),
        (actor_factories.wolf, 20),
        (actor_factories.werewolf, 5),
    ],
    6: [(actor_factories.vampire, 10), (actor_factories.hound, 40)],
    7: [
        (actor_factories.ghoul, 40),
        (actor_factories.brute_zombie, 35),
        (actor_factories.hound, 35),
        (actor_factories.werewolf, 10),
    ],
}


fixed_item_by_floor: Dict[int, List[Tuple[Entity, int]]] = {
    1: [
        (item_factories.health_potion, 1),
    ],
    2: [
        (item_factories.health_potion, 2),
    ],
    3: [
        (item_factories.health_potion, 2),
    ],
    4: [
        (item_factories.great_health_potion, 1),
    ],
    5: [
        (item_factories.great_health_potion, 1),
    ],
}
