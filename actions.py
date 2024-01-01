from __future__ import annotations
import random

from typing import Optional, Tuple, TYPE_CHECKING

import color
from exceptions import Impossible

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item


class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.parent.engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f"You picked up the {item.name}!")
                return

        raise Impossible("There is nothing here to pick up.")


class ItemAction(Action):
    def __init__(
        self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        if self.item.consumable:
            self.item.consumable.activate(self)


class DropItem(ItemAction):
    def perform(self) -> None:
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item)

        self.entity.inventory.drop(self.item)


class EquipAction(Action):
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        self.entity.equipment.toggle_equip(self.item)


class WaitAction(Action):
    def perform(self) -> None:
        pass


class TakeStairsAction(Action):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if (self.entity.x, self.entity.y) == self.engine.game_map.upstairs_location:
            # Ascending
            if (
                len(self.engine.game_world.floors)
                < self.engine.game_world.current_floor + 1
            ):
                # If we're on the last existing floor, we generate a new one.
                self.engine.game_world.current_floor += 1
                self.engine.game_world.generate_floor()
            else:
                self.engine.game_world.load_floor(
                    self.engine.game_world.current_floor + 1
                )

            self.engine.message_log.add_message(
                "You ascend the staircase.", color.ascend
            )
        elif (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            # Descending
            self.engine.game_world.load_floor(self.engine.game_world.current_floor - 1)

            self.engine.message_log.add_message(
                "You descend the staircase.", color.ascend
            )
        else:
            raise Impossible("There are no stairs here.")


class ActionWithDirection(Action):
    """An action with a direction."""

    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination.."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class ActionWithRangedTarget(Action):
    """An action with a ranged targeted entity."""

    def __init__(self, entity: Actor, target_xy: Tuple[int, int]):
        super().__init__(entity)

        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        target = self.engine.game_map.get_actor_at_location(*self.target_xy)

        if target is None:
            raise Impossible("Nothing to target.")
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    @property
    def is_target_clear(self) -> bool:
        """Return True if there are no entities blocking the path to the target."""
        return self.entity.ai.is_line_of_sight_clear(
            self.entity.x, self.entity.y, self.target_actor.x, self.target_actor.y
        )

    def perform(self) -> None:
        raise NotImplementedError()


class MeleeAction(ActionWithDirection):
    """Perform an attack towards a direction."""

    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise Impossible("Nothing to attack.")

        damage = self.entity.fighter.power
        # accuracy = accuracy = 100 * 1.065 ** (weapon net enchant)

        hit_probability = 100 * 0.987 ** (target.fighter.defense)

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"

        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        if hit_probability < random.random() * 100:
            self.engine.message_log.add_message(
                f"{attack_desc} but misses.", attack_color
            )
            return

        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points.", attack_color
            )
            target.fighter.hp -= damage

            # Check if the entity has status effects that can trigger on attack, and apply them.
            if self.entity.status.status_effects:
                for status_effect, chance in self.entity.status.status_effects:
                    if random.random() < chance:
                        status_effect.apply(target)

            if target.fighter.bleeds:
                set_bloody_tiles(self.engine, target)
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.", attack_color
            )


class RangedAttackAction(ActionWithRangedTarget):
    """Perform an attack against a ranged target."""

    def perform(self) -> None:
        if not self.is_target_clear:
            raise Impossible("You have no clear shot!")

        if self.entity is self.engine.player:
            attack_color = color.player_atk
            # only the player gets ranged attack from an item, monsters use the power value.
            attacker_power = self.entity.equipment.ranged_bonus
            ammo = self.entity.equipment.get_ammo_equippable
            ammo.consume()
        else:
            attack_color = color.enemy_atk
            attacker_power = self.entity.fighter.power

        damage = attacker_power - self.target_actor.fighter.defense

        attack_desc = (
            f"{self.entity.name.capitalize()} shots at {self.target_actor.name}"
        )

        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points.", attack_color
            )
            self.target_actor.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.", attack_color
            )


class MovementAction(ActionWithDirection):
    """Action for moving an entity."""

    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        is_grappled = self.entity.status.is_grappled

        if is_grappled:
            raise Impossible("You can't move while being grappled!")

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise Impossible("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination is blocked by a tile.
            raise Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is blocked by an entity.
            raise Impossible("That way is blocked.")

        self.entity.move(self.dx, self.dy)

        if self.engine.game_map.get_item_at_location(dest_x, dest_y):
            self.engine.message_log.add_message(
                f"There is a {self.engine.game_map.get_item_at_location(dest_x, dest_y).name} here."
            )


class BumpAction(ActionWithDirection):
    """This class determines wether the entity moves or attacks."""

    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()

        return MovementAction(self.entity, self.dx, self.dy).perform()


class QuickHealAction(Action):
    """Use a healing item from your inventory."""

    def perform(self) -> None:
        healing_items = self.entity.inventory.healing_items

        if self.entity.fighter.hp == self.entity.fighter.max_hp:
            raise Impossible("Your health is already full.")

        if healing_items:
            # Todo: Maybe use the item that wastes less if it would over heal the player?
            # Get the first item in the list
            item = healing_items[0]
            item.consumable.activate(item.consumable.get_action(self.entity))
        else:
            raise Impossible("You don't have any healing items.")


def set_bloody_tiles(engine: Engine, target: Actor) -> None:
    """Set the bloody tiles position for targeted entities."""
    engine.game_map.bloody_tiles.add((target.x, target.y))
    # Small random chance of adding one adjacent tile to the bloody tile list
    if random.random() < 0.2:
        adjacent_tiles = [
            (target.x + 1, target.y),
            (target.x - 1, target.y),
            (target.x, target.y + 1),
            (target.x, target.y - 1),
        ]
        random_tile = random.choice(adjacent_tiles)
        engine.game_map.bloody_tiles.add(random_tile)
