from __future__ import annotations
from typing import TYPE_CHECKING, Tuple
from components.base_component import BaseComponent
from status_effect import Confused, Grappled


if TYPE_CHECKING:
    from entity import Actor
    from status_effect import StatusEffect


class Status(BaseComponent):
    """Actor component that holds the relevant information to handle combat."""

    parent: Actor

    def __init__(self, status_effects: list[Tuple[StatusEffect, float]] = []):
        # a list of tuples with a status effect that the entity can cause and the chance of triggering
        self.status_effects = status_effects
        # a list of currently active status effects of the entity
        self.active_status_effects: list[StatusEffect] = []

    @property
    def grappled(self) -> bool:
        return any(
            isinstance(effect, Grappled) for effect in self.active_status_effects
        )

    @property
    def confused(self) -> bool:
        return any(
            isinstance(effect, Confused) for effect in self.active_status_effects
        )

    def set_active_status_effect(self, status_effect: StatusEffect):
        self.active_status_effects.append((status_effect))

    def remove_active_status_effect(self, status_effect: StatusEffect):
        self.active_status_effects.remove((status_effect))

    def process_active_effects(self):
        for status_effect in self.active_status_effects:
            status_effect.duration -= 1
            if status_effect.duration <= 0:
                # Run the remove method on the status effect
                status_effect.remove(self.parent)
                # Remove the status effect from the list
                self.active_status_effects.remove(status_effect)
