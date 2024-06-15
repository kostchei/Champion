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

def filter_monsters_by_realm(monsters_by_cr, realm):
    filtered_monsters_by_cr = {}
    for cr, monsters in monsters_by_cr.items():
        filtered_monsters = [
            monster for monster in monsters
            if realm in monster['realm']
        ]
        if filtered_monsters:
            filtered_monsters_by_cr[cr] = filtered_monsters
    return filtered_monsters_by_cr

def find_highest_cr(xp_budget, filtered_monsters_by_cr):
    for cr_info in reversed(challenge_rating_list):
        if cr_info['xp'] <= xp_budget and cr_info['cr'] in filtered_monsters_by_cr:
            return cr_info['cr']
    return 0

def generate_encounter(xp_budget, filtered_monsters_by_cr):
    encounter = []

    def add_to_encounter(monster, cr):
        encounter.append(monster)
        nonlocal xp_budget
        xp_budget -= next(cr_item['xp'] for cr_item in challenge_rating_list if cr_item['cr'] == cr)

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
        cr = find_highest_cr(xp_budget, filtered_monsters_by_cr)
        if cr in filtered_monsters_by_cr:
            selected_monster = random.choice(filtered_monsters_by_cr[cr])
            add_to_encounter(selected_monster, cr)
            xp_budget *= random.uniform(0.5, 1)

    elif method == 2:
        pair_budget = xp_budget / 3
        for _ in range(2):
            cr = find_highest_cr(pair_budget, filtered_monsters_by_cr)
            if cr in filtered_monsters_by_cr:
                selected_monster = random.choice(filtered_monsters_by_cr[cr])
                add_to_encounter(selected_monster, cr)

    elif method == 3:
        minion_budget = xp_budget / 12
        for _ in range(2):
            cr = find_highest_cr(minion_budget, filtered_monsters_by_cr)
            if cr in filtered_monsters_by_cr:
                selected_monster = random.choice(filtered_monsters_by_cr[cr])
                for _ in range(random.randint(1, 6)):
                    add_to_encounter(selected_monster, cr)

    elif method == 4:
        swarm_budget = xp_budget / 60
        for _ in range(3):
            cr = find_highest_cr(swarm_budget, filtered_monsters_by_cr)
            if cr in filtered_monsters_by_cr:
                selected_monster = random.choice(filtered_monsters_by_cr[cr])
                for _ in range(random.randint(1, 10)):
                    add_to_encounter(selected_monster, cr)

    return encounter

def get_party_xp_threshold(party_size, party_level, difficulty):
    for threshold in difficulty_thresholds:
        if threshold['level'] == party_level:
            return threshold[difficulty] * party_size
    return 0

def generate_encounter_data(party_size, party_level, difficulty, terrain, realm, monsters_by_cr):
    filtered_monsters_by_cr = filter_monsters_by_realm(monsters_by_cr, realm)
    
    if difficulty == "random":
        difficulty = random.choices(["easy", "medium", "hard", "deadly"], [0.14, 0.68, 0.13, 0.05])[0]

    xp_budget = get_party_xp_threshold(party_size, party_level, difficulty)
    encounter = generate_encounter(xp_budget, filtered_monsters_by_cr)

    return {
        "encounter": encounter,
        "difficulty": difficulty,
        "xp_budget": xp_budget,
        "terrain": terrain
    }

def save_encounter_data(encounter_data, file_path):
    with open(file_path, 'w') as f:
        json.dump(encounter_data, f, indent=4)

if __name__ == "__main__":
    # Get parameters from command line arguments
    party_size = int(sys.argv[1])
    party_level = int(sys.argv[2])
    difficulty = sys.argv[3]
    terrain = sys.argv[4]
    realm = sys.argv[5]

    # Load monsters data based on the realm
    monsters_by_cr = load_json(os.path.join(base_path, f'../realms/{realm}.json'))

    encounter_data = generate_encounter_data(party_size, party_level, difficulty, terrain, realm, monsters_by_cr)
    save_encounter_data(encounter_data, 'encounter_data.json')
    print(f"Encounter data saved to 'encounter_data.json'")

    # Run combat_gui.py
    subprocess.run([sys.executable, os.path.join(base_path, '../combat_gui.py'), 'encounter_data.json'])
