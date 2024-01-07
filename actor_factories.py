"""Library of different types of entities."""
from components.ai import BasicMeleeEnemyAI, BatAI, StaticRangedEnemy
from components.inventory import Inventory
from components.equipment import Equipment
from components.fighter import Fighter
from components.level import Level
from components.status import Status
from entity import Actor
from status_effect import BloodDrain, Confused, Grappled

player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=None,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=10, base_power=2),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200),
    status=Status(),
)

zombie = Actor(
    char="z",
    color=(63, 127, 63),
    name="Zombie",
    ai_cls=BasicMeleeEnemyAI,
    equipment=Equipment(),
    fighter=Fighter(
        hp=8, base_defense=0, base_power=2, base_accuracy=80, base_speed=70
    ),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35),
    status=Status(status_effects=[(Grappled(), 90)]),
)

# Variant of a zombie with more health and stronger attack
brute_zombie = Actor(
    char="Z",
    color=(0, 127, 0),
    name="Brute Zombie",
    ai_cls=BasicMeleeEnemyAI,
    equipment=Equipment(),
    fighter=Fighter(
        hp=16, base_defense=0, base_power=3, base_accuracy=90, base_speed=60
    ),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=60),
    status=Status(status_effects=[(Grappled(), 90)]),
)

hound = Actor(
    char="h",
    color=(48, 44, 21),
    name="Hound",
    ai_cls=BasicMeleeEnemyAI,
    equipment=Equipment(),
    fighter=Fighter(hp=6, base_defense=15, base_power=3, base_speed=150),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=40),
    status=Status(),
)

wolf = Actor(
    char="w",
    color=(88, 84, 61),
    name="Wolf",
    ai_cls=BasicMeleeEnemyAI,
    equipment=Equipment(),
    fighter=Fighter(hp=6, base_defense=20, base_power=4, base_speed=180),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=50),
    status=Status(),
)

bat = Actor(
    char="b",
    color=(110, 110, 110),
    name="Bat",
    ai_cls=BatAI,
    equipment=Equipment(),
    fighter=Fighter(
        hp=5, base_defense=0, base_power=2, base_accuracy=80, base_speed=110
    ),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=30),
    status=Status(status_effects=[(BloodDrain(heal_amount=1), 90)]),
)

ghoul = Actor(
    char="G",
    color=(0, 127, 0),
    name="Ghoul",
    ai_cls=BasicMeleeEnemyAI,
    equipment=Equipment(),
    fighter=Fighter(hp=14, base_defense=10, base_power=4),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=80),
    status=Status(),
)

skeleton_archer = Actor(
    char="s",
    color=(230, 230, 230),
    remains_color=(160, 160, 160),
    name="Skeleton Archer",
    ai_cls=StaticRangedEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=6, base_defense=0, base_power=1, base_accuracy=60, bleeds=False),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35),
    status=Status(),
)

werewolf = Actor(
    char="W",
    color=(230, 230, 230),
    name="Werewolf",
    ai_cls=BasicMeleeEnemyAI,
    equipment=Equipment(),
    fighter=Fighter(hp=18, base_defense=30, base_power=6, base_speed=150),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=90),
    status=Status(),
)

vampire = Actor(
    char="v",
    color=(63, 127, 63),
    name="Vampire",
    ai_cls=BasicMeleeEnemyAI,
    equipment=Equipment(),
    fighter=Fighter(hp=16, base_defense=20, base_power=5, base_speed=120),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=90),
    status=Status(status_effects=[(BloodDrain(heal_amount=3), 90)]),
)

seducer = Actor(
    char="S",
    color=(220, 20, 60),
    name="Seducer",
    ai_cls=BasicMeleeEnemyAI,
    equipment=Equipment(),
    fighter=Fighter(hp=10, base_defense=10, base_power=3, base_speed=120),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=70),
    status=Status(status_effects=[(Confused(duration=3), 30)]),
)
