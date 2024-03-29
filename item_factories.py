"""Factory functions to create item instances."""
from components import consumable, equippable
from entity import Item
from equipment_types import AmmoType

health_potion = Item(
    char="!",
    color=(127, 0, 255),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=5),
)

great_health_potion = Item(
    char="!",
    color=(147, 40, 255),
    name="Great Health Potion",
    consumable=consumable.HealingConsumable(amount=10),
)

defense_boost_potion = Item(
    char="!",
    color=(0, 255, 255),
    name="Protection Potion",
    consumable=consumable.DefenseBoostConsumable(amount=30, duration=10),
)

power_boost_potion = Item(
    char="!",
    color=(255, 10, 10),
    name="Berserker Potion",
    consumable=consumable.PowerBoostConsumable(amount=3, duration=10),
)

lightning_scroll = Item(
    char="~",
    color=(255, 255, 0),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5),
)

confusion_scroll = Item(
    char="~",
    color=(207, 63, 255),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=6),
)

map_scroll = Item(
    char="~",
    color=(255, 255, 255),
    name="Magic Map",
    consumable=consumable.MapRevealingConsumable(),
)

holy_water_vial = Item(
    char="!",
    color=(220, 220, 255),
    name="Holy Water Vial",
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
    equippable=equippable.Dagger(damage=(1, 3)),
)

spear = Item(
    char="/",
    color=(90, 191, 255),
    name="Spear",
    equippable=equippable.Spear(damage=(2, 4)),
)

sword = Item(
    char="/",
    color=(0, 191, 255),
    name="Sword",
    equippable=equippable.Sword(damage=(3, 6)),
)

broad_sword = Item(
    char="/",
    color=(10, 200, 255),
    name="Broad Sword",
    equippable=equippable.Sword(damage=(4, 8)),
)

axe = Item(
    char="/", color=(0, 191, 255), name="Axe", equippable=equippable.Axe(damage=(3, 6))
)

bow = Item(
    char=")", color=(80, 191, 255), name="Bow", equippable=equippable.Bow(damage=(1, 3))
)

crossbow = Item(
    char=")",
    color=(80, 191, 175),
    name="Crossbow",
    equippable=equippable.Bow(ammo_type=AmmoType.BOLT, damage=(2, 4)),
)

arrows = Item(
    char="=", color=(80, 191, 255), name="Arrows", equippable=equippable.Arrows()
)

bolts = Item(
    char="=",
    color=(80, 191, 175),
    name="Bolts",
    equippable=equippable.Arrows(ammo_type=AmmoType.BOLT, amount=15),
)

leather_armor = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Armor",
    equippable=equippable.LeatherArmor(),
)

chain_mail = Item(
    char="[", color=(139, 69, 19), name="Chain Mail", equippable=equippable.ChainMail()
)


plate_armor = Item(
    char="[",
    color=(139, 69, 19),
    name="Plate Armor",
    equippable=equippable.PlateArmor(),
)
