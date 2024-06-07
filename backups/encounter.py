# encounter.py
import json
import os
import random
import sys
import subprocess
import pygame as pg

# Constants
ENCOUNTER_PROBABILITY = 0.1
ENCOUNTERS_DIR = "encounters"

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def generate_encounter(player_name, hex_coordinates):
    # Generate random stats for the encounter
    encounter_data = {
        "player": player_name,
        "hex": hex_coordinates,
        "monsters": [
            {
                "name": "Goblin",
                "hit_points": random.randint(5, 15),
                "attack_bonus": random.randint(1, 5),
                "damage": f"{random.randint(1, 6)}d6"
            }
        ]
    }

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

def check_for_encounter(player_name, hex_coordinates):
    if random.random() < ENCOUNTER_PROBABILITY:
        generate_encounter(player_name, hex_coordinates)
        return True
    return False

if __name__ == "__main__":
    player_name = sys.argv[1]
    hex_coordinates = eval(sys.argv[2])  # Assuming hex_coordinates are passed as a string representation of a list
    check_for_encounter(player_name, hex_coordinates)
