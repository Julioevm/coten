import datetime
import os

from engine import Engine
from entity import Actor

GRAVEYARD_FILE = "graveyard.txt"


def check_graveyard_file_exists():
    root_dir = os.getcwd()  # Get the current working directory
    graveyard_file = os.path.join(
        root_dir, GRAVEYARD_FILE
    )  # Assuming the file name is "graveyard.txt"

    if os.path.isfile(graveyard_file):
        return True
    else:
        return False


def create_graveyard_entry(player: Actor, engine: Engine) -> None:
    root_dir = os.getcwd()  # Get the current working directory
    graveyard_file = os.path.join(
        root_dir, GRAVEYARD_FILE
    )  # Assuming the file name is "graveyard.txt"

    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(graveyard_file, "a") as file:
        file.write(
            f"+ Player Exp: {player.level.total_xp} Turns: {engine.current_turn} Died at floor {engine.game_world.current_floor} on {current_date} +\n"
        )
