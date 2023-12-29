"""Library of different types of entities."""
from components.ai import HostileEnemy, StaticRangedEnemy
from components.inventory import Inventory
from components.equipment import Equipment
from components.fighter import Fighter
from components.level import Level
from entity import Actor

player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=1, base_power=2),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200),
)

zombie = Actor(
    char="z",
    color=(63, 127, 63),
    name="Zombie",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=8, base_defense=0, base_power=2),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35),
)

# Variant of a zombie with more health and stronger attack
brute_zombie = Actor(
    char="Z",
    color=(0, 127, 0),
    name="Brute Zombie",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=16, base_defense=2, base_power=2),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=80),
)

hound = Actor(
    char="h",
    color=(0, 127, 0),
    name="Hound",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=6, base_defense=0, base_power=5),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=50),
)

ghoul = Actor(
    char="G",
    color=(0, 127, 0),
    name="Ghoul",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=14, base_defense=1, base_power=4),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=75),
)

skeleton_archer = Actor(
    char="s",
    color=(0, 127, 0),
    name="Skeleton Archer",
    ai_cls=StaticRangedEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=6, base_defense=1, base_power=2),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=40),
)

werewolf = Actor(
    char="W",
    color=(230, 230, 230),
    name="Werewolf",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=18, base_defense=2, base_power=6),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=160),
)
