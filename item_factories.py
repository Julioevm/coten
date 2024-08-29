"""Factory functions to create item instances."""
from components import consumable, equippable
from entity import Item
from equipment_types import AmmoType
import special_abilities

health_potion = Item(
    char="!",
    color=(127, 0, 255),
    name="Health Potion",
    description="Heals small wounds.",
    consumable=consumable.HealingConsumable(amount=5),
)

great_health_potion = Item(
    char="!",
    color=(147, 40, 255),
    name="Great Health Potion",
    description="Heals moderate wounds.",
    consumable=consumable.HealingConsumable(amount=10),
)

defense_boost_potion = Item(
    char="!",
    color=(0, 255, 255),
    name="Protection Potion",
    description="Concoction that hardens the skin of the drinker temporarily.",
    consumable=consumable.DefenseBoostConsumable(amount=30, duration=10),
)

power_boost_potion = Item(
    char="!",
    color=(255, 10, 10),
    name="Berserker Potion",
    description="Concoction that increases the strength of the drinker temporarily.",
    consumable=consumable.PowerBoostConsumable(amount=3, duration=10),
)

lightning_scroll = Item(
    char="~",
    color=(255, 255, 0),
    name="Lightning Scroll",
    description="""Ancient magic art scroll.
    Summons a bolt of lightning to strike the closest target, causing great damage.""",
    consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5),
)

confusion_scroll = Item(
    char="~",
    color=(207, 63, 255),
    name="Confusion Scroll",
    description="""Ancient magic art scroll.
    These words of power can confuse the mind of the target.""",
    consumable=consumable.ConfusionConsumable(number_of_turns=6),
)

map_scroll = Item(
    char="~",
    color=(255, 255, 255),
    name="Magic Map",
    description="A magic scroll that draws itself mapping the surrounding area.",
    consumable=consumable.MapRevealingConsumable(),
)

holy_water_vial = Item(
    char="!",
    color=(220, 220, 255),
    name="Holy Water Vial",
    description="""A vial of holy water. It splashes a small area, damaging the cursed creatures of the night.
    It is common to keep one of these vials in every household, to keep off unwanted guests.""",
    consumable=consumable.AOEDamageConsumable(
        damage=6,
        radius=2,
        damage_msg="The {0} is splashed by holy water, taking {1} damage!",
    ),
)

fireball_scroll = Item(
    char="~",
    color=(255, 0, 0),
    name="Fireball Scroll",
    description="""Ancient magic art scroll.
    Summons a fireball that explodes engulfing the target in flames.""",   
    consumable=consumable.AOEDamageConsumable(
        damage=12,
        radius=3,
        damage_msg="The {0} is engulfed in a fiery explosion, taking {1} damage!",
        damages_player=True,
    ),
)

dagger = Item(
    char="/",
    color=(0, 191, 255),
    name="Dagger",
    description="A small blade. More of a tool than a weapon.",
    equippable=equippable.Dagger(damage=(1, 3)),
)

spear = Item(
    char="/",
    color=(90, 191, 255),
    name="Spear",
    description="A long weapon with a pointed tip.",
    equippable=equippable.Spear(damage=(2, 4)),
)

sword = Item(
    char="/",
    color=(0, 191, 255),
    name="Sword",
    description="A sharp blade. A common weapon.",
    equippable=equippable.Sword(damage=(3, 6)),
)

broad_sword = Item(
    char="/",
    color=(10, 200, 255),
    name="Broad Sword",
    description="A large sword with a wide blade.",
    equippable=equippable.Sword(damage=(4, 8), special_ability=special_abilities.whirlwind_attack),
)

axe = Item(
    char="/",
    color=(0, 191, 255),
    name="Axe", 
    description="A heavy weapon with a sharp edge.",
    equippable=equippable.Axe(damage=(3, 6), special_ability=special_abilities.whirlwind_attack)
)

bow = Item(
    char=")",
    color=(80, 191, 255),
    name="Bow",
    description="A ranged weapon that uses arrows. Commonly used for hunting.",
    equippable=equippable.Bow(damage=(1, 3))
)

crossbow = Item(
    char=")",
    color=(80, 191, 175),
    name="Crossbow",
    description="A ranged weapon that uses bolts. More powerful than a regular bow.",
    equippable=equippable.Bow(ammo_type=AmmoType.BOLT, damage=(2, 4)),
)

arrows = Item(
    char="=", color=(80, 191, 255),
    name="Arrows",
    description="A quiver of arrows.",
    equippable=equippable.Arrows()
)

bolts = Item(
    char="=",
    color=(80, 191, 175),
    name="Bolts",
    description="A quiver of bolts.",
    equippable=equippable.Arrows(ammo_type=AmmoType.BOLT, amount=15),
)

leather_armor = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Armor",
    description="A set of armor made from leather. It provides basic protection.",
    equippable=equippable.LeatherArmor(),
)

chain_mail = Item(
    char="[",
    color=(139, 69, 19),
    name="Chain Mail",
    description="A set of armor made from interlocking metal rings.",
    equippable=equippable.ChainMail()
)


plate_armor = Item(
    char="[",
    color=(139, 69, 19),
    name="Plate Armor",
    description="A set of heavy armor made from metal plates.",
    equippable=equippable.PlateArmor(),
)
