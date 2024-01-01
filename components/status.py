from __future__ import annotations
from typing import TYPE_CHECKING
from components.base_component import BaseComponent


if TYPE_CHECKING:
    from entity import Actor
    from status_effect import StatusEffect


class Status(BaseComponent):
    """Actor component that holds the relevant information to handle combat."""

    parent: Actor

    def __init__(self, status_effects: list[tuple[StatusEffect, int]] = []):
        self.is_grappled = False
        # a list of tuples with a status effect, chance of triggering
        self.status_effects = status_effects
