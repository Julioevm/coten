from enum import auto, Enum


class EquipmentType(Enum):
    WEAPON = auto()
    RANGED = auto()
    ARMOR = auto()
    AMMO = auto()


class AmmoType(Enum):
    ARROW = auto()
    BOLT = auto()
    BULLET = auto()
