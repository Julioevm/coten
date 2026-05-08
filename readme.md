# Castle of the Eternal Night

[![Build Executable](https://github.com/reave/coten/actions/workflows/build.yml/badge.svg)](https://github.com/reave/coten/actions/workflows/build.yml)

COTEN for short, is a classic roguelike built with python and the libtcod library. It has a castlevania-esque setting, a dark castle filled with creatures of the night, that you have to climb to defeat the evil vampire lord.

## Quick Start

This project uses [UV](https://docs.astral.sh/uv/) for dependency management. Install UV, then:

```bash
uv sync          # install everything
uv run main.py   # launch the game
```

This will:
- Download the correct Python version (3.11.x) if needed
- Create a virtual environment (`.venv/`)
- Install all dependencies (including dev tools like Nuitka)

Or activate the environment and run directly:

```bash
# Windows
.venv\Scripts\activate
python main.py

# macOS / Linux
source .venv/bin/activate
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

### See environment info

```bash
uv run python --version
uv tree
```

### Build a local executable

```bash
uv run nuitka --standalone --onefile --disable-console --include-data-dir=assets=assets --output-filename=coten main.py
```

Note: You can't use Python > 3.11 for the build, as Nuitka does not yet support it.

### CI / CD

Every push to `master` triggers a [GitHub Action](.github/workflows/build.yml) that:
1. Installs UV via `astral-sh/setup-uv`
2. Runs `uv sync --frozen` (uses the lockfile, no network resolution)
3. Builds a standalone executable with Nuitka on macOS, Ubuntu, and Windows
4. Uploads the resulting binaries as build artifacts

You can also trigger the workflow manually from the Actions tab.

### Project files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project metadata, dependencies, UV config |
| `uv.lock` | Lockfile for reproducible installs |
| `.python-version` | Pins Python 3.11.x |
| `.github/workflows/build.yml` | CI pipeline for building executables |
