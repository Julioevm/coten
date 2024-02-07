"""Parameters for different settings of the dungeon generation."""

from __future__ import annotations
from typing import Dict, List, Tuple, TYPE_CHECKING
import actor_factories
import item_factories
from map_gen import encounter_factories

if TYPE_CHECKING:
    from entity import Entity
    from map_gen.encounter import Encounter

# These parameters are used up to the next floor in the lists.
# Something in floor 1 will be used in floor 2, etc.
# Unless you override the values in the lists.
max_room_items_by_floor = [
    (1, 1),
    (4, 2),
]

max_room_monsters_by_floor = [
    (1, 1),
    (2, 2),
    (4, 3),
    (6, 5),
]

max_items_by_floor = [
    (1, 10),
    (3, 20),
    (5, 30),
]

max_monsters_by_floor = [
    (1, 20),
    (3, 30),
    (5, 40),
    (7, 50),
]

max_encounters_by_floor = [
    (1, 1),
    (3, 2),
    (4, 2),
    (5, 3),
    (7, 4),
]

# These parameters are used up to the next floor in the lists.
# Something in floor 1 will be used in floor 2, etc.
# Unless you override the weights in the lists.
# To remove an item, set its weight to 0.
item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [
        (item_factories.health_potion, 30),
        (item_factories.defense_boost_potion, 15),
        (item_factories.power_boost_potion, 10),
        (item_factories.holy_water_vial, 10),
        (item_factories.map_scroll, 4),
    ],
    2: [
        (item_factories.bow, 15),
        (item_factories.arrows, 20),
        (item_factories.confusion_scroll, 10),
        (item_factories.spear, 5),
        (item_factories.leather_armor, 15),
    ],
    3: [
        (item_factories.fireball_scroll, 5),
        (item_factories.chain_mail, 5),
        (item_factories.axe, 5),
        (item_factories.holy_water_vial, 15),
    ],
    4: [
        (item_factories.crossbow, 5),
        (item_factories.bolts, 10),
        (item_factories.lightning_scroll, 10),
        (item_factories.sword, 5),
        (item_factories.great_health_potion, 15),
    ],
    5: [
        (item_factories.fireball_scroll, 10),
        (item_factories.plate_armor, 5),
        (item_factories.leather_armor, 5),
    ],
    6: [
        (item_factories.fireball_scroll, 25),
        (item_factories.chain_mail, 15),
        (item_factories.broad_sword, 5),
    ],
}

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [
        (actor_factories.zombie, 80),
        (actor_factories.bat, 20),
    ],
    1: [(actor_factories.skeleton_archer, 20)],
    2: [
        (actor_factories.bat, 5),
        (actor_factories.hound, 5),
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

# This is explicit per level, they don't carry over.
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


floor_encounters: Dict[int, List[Tuple[Encounter, int]]] = {
    1: [(encounter_factories.zombie_mob, 90)],
    2: [(encounter_factories.hound_pack, 30), (encounter_factories.zombie_mob, 90)],
}
