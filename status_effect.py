from __future__ import annotations

from typing import TYPE_CHECKING

import color

if TYPE_CHECKING:
    from entity import Actor


class StatusEffect:
    def __init__(self, name: str, duration: int):
        self.name = name
        self.duration = duration

    def apply(self, entity: Actor, target: Actor):
        raise NotImplementedError()

    def remove(self, entity: Actor):
        raise NotImplementedError()


class Grappled(StatusEffect):
    def __init__(self, duration=1):
        super().__init__("grappled", duration)

    def apply(self, entity: Actor, target: Actor):
        engine = entity.parent.engine
        # check if the entity is the player
        if target is engine.player and not target.status.grappled:
            engine.message_log.add_message("You are being grappled!", color.yellow)
        target.status.set_active_status_effect(self, self.duration)

    def remove(self, entity: Actor):
        entity.status.grappled = 0


class BloodDrain(StatusEffect):
    def __init__(self, heal_amount: int, duration=0):
        self.heal_amount = heal_amount
        super().__init__("blood drain", duration)

    def apply(self, entity: Actor, target: Actor):
        engine = entity.parent.engine
        entity.fighter.heal(self.heal_amount)
        if target is engine.player:
            engine.message_log.add_message(
                "{entity.name} is draining your blood!", color.yellow
            )

    def remove(self, entity: Actor):
        entity.status.grappled = 0
