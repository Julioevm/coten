from __future__ import annotations
from typing import TYPE_CHECKING
from components.base_component import BaseComponent


if TYPE_CHECKING:
    from entity import Actor


class Status(BaseComponent):
    """Actor component that holds the relevant information to handle combat."""

    parent: Actor

    def __init__(self):
        self.is_grappled = False
