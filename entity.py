from __future__ import annotations

import copy
import math
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union

from render_order import RenderOrder

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.consumable import Consumable
    from components.equippable import Equippable
    from components.equipment import Equipment
    from components.fighter import Fighter
    from components.inventory import Inventory
    from components.level import Level
    from components.status import Status
    from game_map import GameMap

T = TypeVar("T", bound="Entity")


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    parent: Union[GameMap, Inventory]

    def __init__(
        self,
        parent: Optional[GameMap] = None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order

        if parent:
            # If parent isn't provided now then it will be set later.
            self.parent = parent
            parent.entities.add(self)

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    def spawn(self: T, x: int, y: int, gamemap: GameMap) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        gamemap.entities.add(clone)

        if isinstance(self, Actor):
            gamemap.engine.turn_manager.add_actor(clone)
        return clone

    def move(self, dx: int, dy: int) -> None:
        """Move the entity by a given amount."""
        self.x += dx
        self.y += dy

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        """Place this entity at a new location.  Handles moving across GameMaps."""
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "parent"):  # Possibly uninitialized.
                if self.parent is self.gamemap:
                    self.gamemap.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        """
        Return the distance between the current entity and the given (x, y) coordinate.
        """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)


class Actor(Entity):
    """An entity that can act."""

    _id_counter = 0

    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        remains_color: Tuple[int, int, int] = (191, 0, 0),
        name="<Unnamed>",
        ai_cls: Type[BaseAI] | None,
        equipment: Equipment,
        fighter: Fighter,
        inventory: Inventory,
        level: Level,
        status: Status,
        is_alive=True,
    ):
        self.id = Actor._id_counter
        self.is_alive = is_alive
        Actor._id_counter += 1
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
        )

        if ai_cls is not None:
            self.original_ai = ai_cls
            self.ai = ai_cls(self)
        else:
            self.original_ai = None
            self.ai = None

        self.equipment: Equipment = equipment
        self.equipment.parent = self

        self.fighter = fighter
        self.fighter.parent = self

        self.inventory = inventory
        self.inventory.parent = self

        self.level = level
        self.level.parent = self

        self.status = status
        self.status.parent = self

        self.remains_color = remains_color

    def __copy__(self):
        # Create a shallow copy of the actor
        cls = self.__class__
        new_actor = cls.__new__(cls)
        new_actor.__dict__.update(self.__dict__)

        # Assign a new unique ID
        new_actor.id = Actor._id_counter
        Actor._id_counter += 1

        return new_actor

    def __deepcopy__(self, memo):
        # Create a deep copy of the actor
        cls = self.__class__
        new_actor = cls.__new__(cls)
        memo[id(self)] = new_actor

        for k, v in self.__dict__.items():
            setattr(new_actor, k, copy.deepcopy(v, memo))

        # Assign a new unique ID
        new_actor.id = Actor._id_counter
        Actor._id_counter += 1

        return new_actor

    def restore_ai(self):
        """Restore the original AI."""
        if self.original_ai:
            self.ai = self.original_ai(self)
        else:
            self.ai = None


class Item(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        consumable: Optional[Consumable] = None,
        equippable: Optional[Equippable] = None,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
        )

        self.consumable = consumable
        if self.consumable:
            self.consumable.parent = self

        self.equippable = equippable

        if self.equippable:
            self.equippable.parent = self
