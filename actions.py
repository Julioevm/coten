from __future__ import annotations
import random

from typing import Optional, Tuple, TYPE_CHECKING

import color
import tile_types
from entity import Actor
from exceptions import Impossible
from global_vars import HIT_CHANCE_BASE
from map_gen.map_utils import set_bloody_tiles

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item


class Action:
    def __init__(self, entity: Actor) -> None:
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.parent.engine

    def __repr__(self) -> str:
        return f"{self.__class__} by {self.entity.name}"

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class EnergyAction(Action):
    """An action with an energy cost. Most actor actions will inherit from this."""

    def __init__(self, entity: Actor, cost: int = 100) -> None:
        super().__init__(entity=entity)
        self.cost = cost

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.parent.engine

    @property
    def can_perform(self) -> bool:
        return self.entity.fighter.energy >= self.cost

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()

    def exhaust_energy(self) -> None:
        self.entity.fighter.energy -= self.cost


class VictoryAction(Action):
    def perform(self) -> None:
        self.engine.victory = True


class PickupAction(EnergyAction):
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


class ItemAction(EnergyAction):
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


class EquipAction(EnergyAction):
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        self.entity.equipment.toggle_equip(self.item)


class WaitAction(EnergyAction):
    def perform(self) -> None:
        pass


class MoveToTileAction(EnergyAction):
    def __init__(self, entity: Actor, tile_x: int, tile_y: int):
        super().__init__(entity)
        self.tile_x = tile_x
        self.tile_y = tile_y

    def perform(self) -> None:
        from components.ai import MoveToTile

        self.entity.ai = MoveToTile(self.entity, self.tile_x, self.tile_y)
        # Get the action and perform it in the same turn we set the AI for subsequent turns
        # otherwise the turn will be 'lost' just setting the AI.
        action = self.entity.ai.get_action()
        if action is not None:
            action.perform()


class TakeStairsAction(EnergyAction):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if (self.entity.x, self.entity.y) == self.engine.game_map.upstairs_location:
            self.engine.game_world.ascend()
        elif (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.engine.game_world.descend()
        else:
            raise Impossible("There are no stairs here.")


class ActionWithDirection(EnergyAction):
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


class ActionWithRangedTarget(EnergyAction):
    """An action with a ranged targeted entity."""

    def __init__(self, entity: Actor, target_xy: Tuple[int, int]):
        super().__init__(entity)

        self.target_xy = target_xy

    @property
    def target_actor(self) -> Actor:
        """Return the actor at this actions destination."""
        target = self.engine.game_map.get_actor_at_location(*self.target_xy)

        if target is None:
            raise Impossible("Nothing to target.")
        return target

    @property
    def is_target_clear(self) -> bool:
        """Return True if there are no entities blocking the path to the target."""
        return self.engine.game_map.is_line_of_sight_clear(
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

        damage = self.entity.fighter.melee_damage
        # accuracy = accuracy = 100 * 1.065 ** (weapon net enchant)

        hit_probability = self.entity.fighter.accuracy * HIT_CHANCE_BASE ** (
            target.fighter.defense
        )

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
                        status_effect.apply(target=target, entity=self.entity)

            if target.fighter.bleeds:
                set_bloody_tiles(self.engine, target)
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.", attack_color
            )


class RangedAttackAction(ActionWithRangedTarget):
    """Perform an attack against a ranged target."""

    def perform(self) -> None:
        target = self.target_actor

        if not self.is_target_clear:
            raise Impossible("You have no clear shot!")

        if target is self.entity:
            raise Impossible("You cannot attack yourself!")

        if self.entity is self.engine.player:
            attack_color = color.player_atk
            # only the player gets ranged attack from an item, monsters use the power value.
            attacker_power = (
                self.entity.equipment.ranged_damage + self.entity.equipment.ranged_bonus
            )
            ammo = self.entity.equipment.get_ammo_equippable
            if ammo:
                ammo.consume()
        else:
            attack_color = color.enemy_atk
            attacker_power = self.entity.fighter.melee_damage

        damage = attacker_power

        # get distance from target to entity
        distance = self.entity.distance(*self.target_xy)

        # ranged attacks get a small penalty to accuracy based on distance
        hit_probability = self.entity.fighter.accuracy * HIT_CHANCE_BASE ** (
            target.fighter.defense + (distance * 2)
        )

        attack_desc = (
            f"{self.entity.name.capitalize()} shots at {self.target_actor.name}"
        )

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
                        status_effect.apply(target=target, entity=self.entity)

            if target.fighter.bleeds:
                set_bloody_tiles(self.engine, target)
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.", attack_color
            )


class PounceAction(ActionWithRangedTarget):
    """Pounce towards a ranged target."""

    def __init__(
        self, entity: Actor, target_xy: Tuple[int, int], next_to_target: Tuple[int, int]
    ):
        super().__init__(entity, target_xy)
        self.next_to_target = next_to_target

    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise Impossible("Nothing to attack.")

        damage = self.entity.fighter.melee_damage

        hit_probability = self.entity.fighter.accuracy * HIT_CHANCE_BASE ** (
            target.fighter.defense
        )

        attack_desc = (
            f"{self.entity.name.capitalize()} fiercely pounds at {target.name}!"
        )

        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        # Move the attacker next to the player
        self.entity.x = self.next_to_target[0]
        self.entity.y = self.next_to_target[1]

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

            if target.fighter.bleeds:
                set_bloody_tiles(self.engine, target)
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.", attack_color
            )


class MovementAction(ActionWithDirection):
    """Action for moving an entity."""

    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        is_grappled = self.entity.status.grappled

        if is_grappled:
            raise Impossible("You can't move while being grappled!")

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise Impossible("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # check if the tile is of type door

            if self.engine.game_map.tiles[dest_x, dest_y] == tile_types.closed_door:
                return OpenDoorAction(self.entity, dest_x, dest_y).perform()
            # Destination is blocked by a tile.
            raise Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is blocked by an entity.
            raise Impossible("That way is blocked.")

        self.entity.move(self.dx, self.dy)

        item = self.engine.game_map.get_item_at_location(dest_x, dest_y)
        if self.entity is self.engine.player and item is not None:
            self.engine.message_log.add_message(f"There is a {item.name} here.")


class BumpAction(ActionWithDirection):
    """This class determines wether the entity moves or attacks."""

    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()

        return MovementAction(self.entity, self.dx, self.dy).perform()


class OpenDoorAction(ActionWithDirection):
    """This class opens a door."""

    def perform(self) -> None:
        if self.engine.game_map.tiles["walkable"][self.dx, self.dy]:
            raise Impossible("The door is already open!")
        if self.engine.game_map.tiles[self.dx, self.dy] == tile_types.closed_door:
            self.engine.game_map.tiles[self.dx, self.dy] = tile_types.open_door
            self.engine.message_log.add_message("You opened the door.")
        else:
            raise Impossible("The door is already open!")


class QuickHealAction(EnergyAction):
    """Use a healing item from your inventory."""

    def perform(self) -> None:
        healing_items = self.entity.inventory.healing_items

        if self.entity.fighter.hp == self.entity.fighter.max_hp:
            raise Impossible("Your health is already full.")

        if healing_items:
            # Todo: Maybe use the item that wastes less if it would over heal the player?
            # Get the first item in the list
            item = healing_items[0]
            if item.consumable is not None:
                action = item.consumable.get_action(self.entity)
                if isinstance(action, ItemAction):
                    item.consumable.activate(action)
                else:
                    raise Impossible("Invalid action for the item.")
            else:
                raise Impossible("The item cannot be activated.")
        else:
            raise Impossible("You don't have any healing items.")


class SpawnEnemiesAction(EnergyAction):
    def __init__(
        self,
        entity: Actor,
        enemy: Actor,
        area: int = 4,
        number: int = 1,
        cost: int = 100,
    ) -> None:
        self.enemy = enemy
        self.area = area
        self.number = number
        super().__init__(entity, cost)

    def perform(self) -> None:
        # pick random number of empty walkable tiles within 'area' tiles
        game_map = self.entity.gamemap
        max_retries = 10
        for _ in range(self.number):
            valid = False
            tries = 0  # Limit number of tries before giving up in case the are cant fit the enemies
            while not valid and max_retries > tries:
                tries += 1
                x = random.randint(self.entity.x - self.area, self.entity.x + self.area)
                y = random.randint(self.entity.y - self.area, self.entity.y + self.area)

                if (
                    self.engine.game_map.in_bounds(x, y)
                    and self.engine.game_map.tiles["walkable"][x, y]
                    and not self.engine.game_map.get_blocking_entity_at_location(x, y)
                ):
                    valid = True
                    self.enemy.spawn(x, y, game_map)
