from __future__ import annotations

import random
from typing import List, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod
from actions import (
    Action,
    BumpAction,
    MeleeAction,
    MovementAction,
    RangedAttackAction,
    WaitAction,
)

if TYPE_CHECKING:
    from entity import Actor


class BaseAI(Action):
    def get_action(self) -> Action:
        raise NotImplementedError()

    def perform(self) -> None:
        self.get_action().perform()

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.
        cost = np.array(self.entity.parent.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.parent.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[entity.x, entity.y] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]


class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for a given number of turns, then revert back to its previous AI.
    If an actor occupies a tile it is randomly moving into, it will attack.
    """

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def get_action(self) -> Action:
        # Pick a random direction
        direction_x, direction_y = random.choice(
            [
                (-1, -1),  # Northwest
                (0, -1),  # North
                (1, -1),  # Northeast
                (-1, 0),  # West
                (1, 0),  # East
                (-1, 1),  # Southwest
                (0, 1),  # South
                (1, 1),  # Southeast
            ]
        )

        # The actor will either try to move or attack in the chosen random direction.
        # Its possible the actor will just bump into the wall, wasting a turn.
        return BumpAction(
            self.entity,
            direction_x,
            direction_y,
        )


class BasicMeleeEnemyAI(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

    def get_action(self) -> Action:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))  # Chebyshev distance.

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy)

            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity,
                dest_x - self.entity.x,
                dest_y - self.entity.y,
            )

        return WaitAction(self.entity)


class StaticRangedEnemy(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

    def get_action(self) -> Action:
        target = self.engine.player

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            return RangedAttackAction(self.entity, (target.x, target.y))

        return WaitAction(self.entity)
