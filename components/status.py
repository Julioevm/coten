from __future__ import annotations
from typing import TYPE_CHECKING, Tuple
from components.base_component import BaseComponent
from status_effect import Grappled


if TYPE_CHECKING:
    from entity import Actor
    from status_effect import StatusEffect


class Status(BaseComponent):
    """Actor component that holds the relevant information to handle combat."""

    parent: Actor

    def __init__(self, status_effects: list[Tuple[StatusEffect, int]] = []):
        # a list of tuples with a status effect, chance of triggering
        self.status_effects = status_effects
        # a list of currently active status effects of the entity, a tuple of the effect and its remaining duration
        self.active_status_effects: list[Tuple[StatusEffect, int]] = []

    @property
    def grappled(self) -> bool:
        return any(
            isinstance(effect, Grappled) for effect, _ in self.active_status_effects
        )

    def set_active_status_effect(self, status_effect: StatusEffect, duration: int):
        self.active_status_effects.append((status_effect, duration))

    def process_active_effects(self):
        for status_effect, duration in self.active_status_effects:
            status_effect.duration -= 1
            if status_effect.duration <= 0:
                self.active_status_effects.remove((status_effect, duration))
