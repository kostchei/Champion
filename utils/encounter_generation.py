import json
import random
import sys
import os
import subprocess
from dice import roll_dice

# Function to load JSON data from a file
def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return {}

# Define the base path
base_path = os.path.dirname(os.path.abspath(__file__))

# Load global data using the base path
difficulty_thresholds = load_json(os.path.join(base_path, '../data/difficulty_thresholds.json'))
challenge_rating_list = load_json(os.path.join(base_path, '../data/challenge_rating_list.json'))

# Function to get XP from CR
def get_xp_from_cr(cr):
    for cr_info in challenge_rating_list:
        if cr_info['cr'] == cr:
            return cr_info['xp']
    return 0

# Updated find_highest_cr function
def find_highest_cr(xp_budget, monsters):
    eligible_monsters = [monster for monster in monsters if get_xp_from_cr(monster['cr']) <= xp_budget]
    if not eligible_monsters:
        return None
    highest_cr = max(monster['cr'] for monster in eligible_monsters)
    highest_cr_monsters = [monster for monster in eligible_monsters if monster['cr'] == highest_cr]
    return random.choice(highest_cr_monsters)

def generate_encounter(xp_budget, monsters):
    encounter = []

    def add_to_encounter(monster):
        encounter.append(monster)
        nonlocal xp_budget
        xp_budget -= get_xp_from_cr(monster['cr'])

    # Check feasible methods based on the XP budget
    feasible_methods = [1]  # Method 1 (Single high CR monster) is always possible

    if xp_budget >= 30:
        feasible_methods.append(2)  # Method 2 (Pair of monsters)
    if xp_budget >= 120:
        feasible_methods.append(3)  # Method 3 (Minions)
    if xp_budget >= 600:
        feasible_methods.append(4)  # Method 4 (Swarm)

    method = random.choice(feasible_methods)

    if method == 1:
        monster = find_highest_cr(xp_budget, monsters)
        if monster:
            add_to_encounter(monster)
            xp_budget *= random.uniform(0.5, 1)

    elif method == 2:
        pair_budget = xp_budget / 3
        for _ in range(2):
            monster = find_highest_cr(pair_budget, monsters)
            if monster:
                add_to_encounter(monster)

    elif method == 3:
        minion_budget = xp_budget / 12
        for _ in range(2):
            monster = find_highest_cr(minion_budget, monsters)
            if monster:
                for _ in range(random.randint(1, 6)):
                    add_to_encounter(monster)

    elif method == 4:
        swarm_budget = xp_budget / 60
        for _ in range(3):
            monster = find_highest_cr(swarm_budget, monsters)
            if monster:
                for _ in range(random.randint(1, 10)):
                    add_to_encounter(monster)

    return encounter

def get_party_xp_threshold(party_size, party_level, difficulty):
    for threshold in difficulty_thresholds:
        if threshold['level'] == party_level:
            return threshold[difficulty] * party_size
    return 0

def generate_encounter_data(party_size, party_level, difficulty, terrain, realm, encounter_number):
    monsters_data = load_json(os.path.join(base_path, f'../realms/{realm}.json'))
    monsters = monsters_data.get('monster', [])
    
    if difficulty == "random":
        difficulty = random.choices(["easy", "medium", "hard", "deadly"], [0.14, 0.68, 0.13, 0.05])[0]

    xp_budget = get_party_xp_threshold(party_size, party_level, difficulty)
    encounter = generate_encounter(xp_budget, monsters)

    file_name = f'Enc{encounter_number}.json'
    file_path = os.path.join(base_path, file_name)
    
    with open(file_path, 'w') as f:
        json.dump({
            "encounter": encounter,
            "difficulty": difficulty,
            "xp_budget": xp_budget,
            "terrain": terrain
        }, f, indent=4)
    print(f"Encounter data saved to '{file_name}'")
    return file_path

if __name__ == "__main__":
    # Get parameters from command line arguments
    party_size = int(sys.argv[1])
    party_level = int(sys.argv[2])
    difficulty = sys.argv[3]
    terrain = sys.argv[4]
    realm = sys.argv[5]

    # Find the next encounter number
    encounter_number = 1
    while os.path.exists(os.path.join(base_path, f'Enc{encounter_number}.json')):
        encounter_number += 1

    encounter_file_path = generate_encounter_data(party_size, party_level, difficulty, terrain, realm, encounter_number)

    # Run combat_gui.py and pass the realm as an argument
    subprocess.run([sys.executable, os.path.join(base_path, '../combat_gui.py'), encounter_file_path, realm])
