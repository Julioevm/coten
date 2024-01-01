from __future__ import annotations

from typing import TYPE_CHECKING

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
        # Todo: Add a message to the log
        entity.status.is_grappled = True

    def remove(self, entity: Actor):
        entity.status.is_grappled = False
