from typing import Dict, List, Tuple
import entity_factories

from entity import Entity

# if TYPE_CHECKING:

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
    0: [(entity_factories.health_potion, 35), (entity_factories.dagger, 10)],
    2: [(entity_factories.confusion_scroll, 10), (entity_factories.leather_armor, 10)],
    4: [(entity_factories.lightning_scroll, 25), (entity_factories.sword, 5)],
    6: [(entity_factories.fireball_scroll, 25), (entity_factories.chain_mail, 15)],
}

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.zombie, 80), (entity_factories.hound, 10)],
    3: [
        (entity_factories.ghoul, 15),
        (entity_factories.brute_zombie, 15),
        (entity_factories.hound, 15),
    ],
    5: [
        (entity_factories.ghoul, 30),
        (entity_factories.brute_zombie, 30),
        (entity_factories.hound, 30),
        (entity_factories.werewolf, 5),
    ],
    7: [
        (entity_factories.ghoul, 40),
        (entity_factories.brute_zombie, 35),
        (entity_factories.hound, 35),
        (entity_factories.werewolf, 10),
    ],
}
