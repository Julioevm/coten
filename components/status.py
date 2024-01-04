from __future__ import annotations
from typing import TYPE_CHECKING, Tuple
from components.base_component import BaseComponent


if TYPE_CHECKING:
    from entity import Actor
    from status_effect import StatusEffect


class Status(BaseComponent):
    """Actor component that holds the relevant information to handle combat."""

    parent: Actor

    def __init__(self, status_effects: list[Tuple[StatusEffect, int]] = []):
        self.is_grappled = 0
        # a list of tuples with a status effect, chance of triggering
        self.status_effects = status_effects

    @property
    def grappled(self) -> bool:
        return self.is_grappled > 0

    @grappled.setter
    def grappled(self, duration: int):
        self.is_grappled = duration

    def process_active_effects(self):
        # As we add more we might keep them in a list and iterate.
        if self.grappled:
            self.is_grappled -= 1
