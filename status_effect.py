from __future__ import annotations

from typing import TYPE_CHECKING

import color

if TYPE_CHECKING:
    from entity import Actor


class StatusEffect:
    def __init__(self, name: str, duration: int):
        self.name = name
        self.duration = duration

    def apply(self, entity: Actor):
        raise NotImplementedError()

    def remove(self, entity: Actor):
        raise NotImplementedError()


class Grappled(StatusEffect):
    def __init__(self, duration=1):
        super().__init__("grappled", duration)

    def apply(self, entity: Actor):
        engine = entity.parent.engine
        # check if the entity is the player
        if entity is engine.player and not entity.status.grappled:
            engine.message_log.add_message("You are being grappled!", color.yellow)
        entity.status.grappled = self.duration

    def remove(self, entity: Actor):
        entity.status.grappled = 0
