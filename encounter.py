import json
import os
import random
import sys
import subprocess
import pygame as pg

# Add the utils directory to the Python path
script_dir = os.path.abspath(os.path.dirname(__file__))
utils_dir = os.path.join(script_dir, "utils")
sys.path.append(utils_dir)

from Champion.utils.old.encounter_generation import generate_encounter_data, load_json
from utils.dice import roll_dice  # Ensure dice is imported from utils
# Constants
ENCOUNTER_PROBABILITY = 0.1
ENCOUNTERS_DIR = "encounters"

def save_json(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def generate_encounter(player_name, hex_coordinates, party_size, party_level, realm):
    monsters_by_cr = load_json('data/monsters_by_cr.json')

    encounter_data = generate_encounter_data(party_size, party_level, "random", realm, monsters_by_cr)

    encounter_data["player"] = player_name
    encounter_data["hex"] = hex_coordinates

    # Save the encounter data to a file
    hex_coordinates_str = "_".join(map(str, hex_coordinates))  # Convert coordinates to string
    encounter_filename = f"encounter_{player_name}_{hex_coordinates_str}.json"
    encounter_filepath = os.path.join(ENCOUNTERS_DIR, encounter_filename)
    save_json(encounter_data, encounter_filepath)

    # Launch the combat GUI
    run_script("combat_gui.py", encounter_filepath)

def run_script(script_name, *args):
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
    subprocess.run([sys.executable, script_path, *args])

def check_for_encounter(player_name, hex_coordinates, party_size, party_level, realm):
    if random.random() < ENCOUNTER_PROBABILITY:
        generate_encounter(player_name, hex_coordinates, party_size, party_level, realm)
        return True
    return False

if __name__ == "__main__":
    player_name = sys.argv[1]
    hex_coordinates = eval(sys.argv[2])  # Assuming hex_coordinates are passed as a string representation of a list
    party_size = 2
    party_level = 1
    terrain = "forest"
    realm = "Elvish"

    check_for_encounter(player_name, hex_coordinates, party_size, party_level, realm)
