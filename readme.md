# Castle of the Eternal Night 

COTEN for short, is a classic roguelike built with python and the libtcod library. It has a castlevania-esque setting, a dark castle filled with creatures of the night, that you have to climb to defeat the evil vampire lord.

## Requirements

Run `pip install -r requirements.txt` to install the necessary dependencies.

## Play

Run `python main.py`

### Controls

Arrows, VIM keys and numpad for movement.

F1 show help menu

. Wait turn

i Inventory

g grab item

d drop item

c character sheet

f shot ranged weapon

/ inspect surroundings (also mouse pointer)

q quick heal (uses a potion from the inventory)

< and > go downstairs or upstairs


## Develop

You can build a local executable with the following command:

`nuitka --standalone --onefile --disable-console --include-data-dir=assets=assets --output-filename=coten  main.py`

Note: You cant use python > 3.11 for the build, as it is not yet supported.