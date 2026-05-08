# Castle of the Eternal Night

COTEN for short, is a classic roguelike built with python and the libtcod library. It has a castlevania-esque setting, a dark castle filled with creatures of the night, that you have to climb to defeat the evil vampire lord.

## Requirements

This project uses [UV](https://docs.astral.sh/uv/) for dependency management. Install UV, then:

```bash
uv sync
```

This will:
- Download the correct Python version (3.11.x) if needed
- Create a virtual environment (`.venv/`)
- Install all dependencies (including dev tools like Nuitka)

## Play

```bash
uv run python main.py
```

Or activate the environment first:

```bash
.venv\Scripts\activate
python main.py
```

### Controls

Mouse: Click anywhere you've explored to move there. Click on items / enemies to interact or attack. Auto-movement will stop when you see an enemy.

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

### Add a dependency

```bash
uv add <package-name>
```

### Update all dependencies

```bash
uv sync --upgrade
```

### Build a local executable

```bash
uv run nuitka --standalone --onefile --disable-console --include-data-dir=assets=assets --output-filename=coten main.py
```

Note: You can't use Python > 3.11 for the build, as Nuitka does not yet support it.

### See environment info

```bash
uv run python --version
uv tree
```
