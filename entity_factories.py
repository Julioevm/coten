"""Dumb entities like decorations."""

from entity import Entity


boulder = Entity(char="o", color=(102, 102, 102), name="boulder", blocks_movement=True)

grave = Entity(char="#", color=(78, 50, 13), name="grave", blocks_movement=False)
