from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from actions import ItemAction
import color
import components.inventory
from components.base_component import BaseComponent
from event_handlers.select_index_handler import (
    AreaRangedAttackHandler,
    SingleRangedAttackHandler,
)
from exceptions import Impossible
from status_effect import Confused

if TYPE_CHECKING:
    from event_handlers.base_event_handler import ActionOrHandler
    from entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        """Try to return the action for this item."""
        return ItemAction(consumer, self.parent)

    def activate(self, action: ItemAction) -> None:
        """Invoke this items ability.

        `action` is the context for this activation.
        """
        raise NotImplementedError()

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, components.inventory.Inventory):
            inventory.items.remove(entity)


class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP!",
                color.health_recovered,
            )
            self.consume()
        else:
            raise Impossible("Your health is already full.")


class DefenseBoostConsumable(Consumable):
    def __init__(self, amount: int, duration: int):
        self.amount = amount
        self.duration = duration

    def activate(self, action: ItemAction) -> None:
        consumer = action.entity
        if consumer.fighter:
            # Apply the defense boost
            consumer.fighter.defense_boost += self.amount
            self.engine.message_log.add_message(
                f"You use the {self.parent.name}, and your defense increases by {self.amount} for {self.duration} turns!",
                color.defense_boost,
            )
            # Schedule the removal of the boost after the duration expires
            self.engine.schedule_effect(
                self.duration, lambda: self.remove_boost(consumer)
            )
            self.consume()
        else:
            raise Impossible("This item cannot be used by this entity.")

    def remove_boost(self, consumer: Actor) -> None:
        # Assuming consumer still exists and has a fighter component
        if consumer and consumer.fighter:
            consumer.fighter.defense_boost -= self.amount
            self.engine.message_log.add_message(
                f"The effect of the {self.parent.name} wears off, and your defense returns to normal.",
                color.boost_fade,
            )


class PowerBoostConsumable(Consumable):
    def __init__(self, amount: int, duration: int):
        self.amount = amount
        self.duration = duration

    def activate(self, action: ItemAction) -> None:
        consumer = action.entity
        if consumer.fighter:
            # Apply the power boost
            consumer.fighter.power_boost += self.amount
            self.engine.message_log.add_message(
                f"You use the {self.parent.name}, and your power increases by {self.amount} for {self.duration} turns!",
                color.power_boost,
            )
            # Schedule the removal of the boost after the duration expires
            self.engine.schedule_effect(
                self.duration, lambda: self.remove_boost(consumer)
            )
            self.consume()
        else:
            raise Impossible("This item cannot be used by this entity.")

    def remove_boost(self, consumer: Actor) -> None:
        # Assuming consumer still exists and has a fighter component
        if consumer and consumer.fighter:
            consumer.fighter.power_boost -= self.amount
            self.engine.message_log.add_message(
                f"The effect of the {self.parent.name} wears off, and your defense returns to normal.",
                color.boost_fade,
            )


class AOEDamageConsumable(Consumable):
    def __init__(
        self,
        damage: int,
        radius: int,
        damage_msg: str,
        damages_player=False,
        needs_target=False,
    ):
        self.damage = damage
        self.radius = radius
        self.damage_msg = damage_msg
        self.damages_player = damages_player
        self.needs_target = needs_target

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")

        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                if not self.damages_player and actor is self.engine.player:
                    continue

                self.engine.message_log.add_message(
                    self.damage_msg.format(actor.name, self.damage)
                )

                actor.fighter.take_damage(self.damage)
                targets_hit = True

        if self.needs_target and not targets_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()


class LightningDamageConsumable(Consumable):
    def __init__(self, damage: int, maximum_range: int):
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            self.engine.message_log.add_message(
                f"A lighting bolt strikes the {target.name} with a loud thunder, for {self.damage} damage!"
            )
            target.fighter.take_damage(self.damage)
            self.consume()
        else:
            raise Impossible("No enemy is close enough to strike.")


class ConfusionConsumable(Consumable):
    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot confuse yourself!")

        self.engine.message_log.add_message(
            f"The eyes of the {target.name} look vacant, as it starts to stumble around!",
            color.status_effect_applied,
        )
        Confused(self.number_of_turns).apply(consumer, target)
        self.consume()


class MapRevealingConsumable(Consumable):
    def activate(self, action: ItemAction) -> None:
        self.engine.message_log.add_message("The map reveals the layout of this floor!")
        self.engine.game_map.reveal_map()
        self.consume()
