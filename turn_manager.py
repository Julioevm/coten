from __future__ import annotations
from typing import TYPE_CHECKING
import heapq

if TYPE_CHECKING:
    from entity import Actor


class TurnManager:
    def __init__(self):
        self.queue = []

    @property
    def has_actors(self):
        return len(self.queue) > 0

    def add_actor(self, actor: Actor):
        heapq.heappush(self.queue, (-actor.fighter.energy, actor.id, actor))

    def get_next_actor(self) -> Actor | None:
        _, _, actor = heapq.heappop(self.queue)
        self.add_actor(actor)
        return actor
