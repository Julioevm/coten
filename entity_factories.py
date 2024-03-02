"""Dumb entities like decorations."""

from entity import Entity


boulder = Entity(char="o", color=(102, 102, 102), name="boulder", blocks_movement=True)

grave = Entity(char="#", color=(78, 50, 13), name="grave", blocks_movement=False)

bones = Entity(char="%", color=(225, 215, 235), name="bones", blocks_movement=False)

shrine = Entity(char="+", color=(255, 215, 0), name="shrine", blocks_movement=True)

torch = Entity(
    char="t", color=(255, 147, 41), name="torch", blocks_movement=False, has_light=True
)

statue = Entity(char="S", color=(192, 192, 192), name="statue", blocks_movement=True)

fountain = Entity(char="F", color=(0, 191, 255), name="fountain", blocks_movement=False)
