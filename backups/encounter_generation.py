# encounter_generator.py
import json
import random
from utils.dice import roll_dice

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

# Load data
terrain_distance_map = load_json('data/terrain_distance_map.json')
monsters_by_cr = load_json('data/monsters_by_cr.json')
difficulty_thresholds = load_json('data/difficulty_thresholds.json')
challenge_rating_list = load_json('data/challenge_rating_list.json')

def generate_encounter_distance(terrain):
    if terrain in terrain_distance_map:
        dice = terrain_distance_map[terrain]['dice']
        multiplier = terrain_distance_map[terrain]['multiplier']
        return roll_dice(dice[0], dice[1]) * multiplier
    return 0

def filter_monsters_by_terrain_and_faction(monsters_by_cr, terrain, faction):
    filtered_monsters_by_cr = {}
    for cr, monsters in monsters_by_cr.items():
        filtered_monsters = [
            monster for monster in monsters
            if terrain in monster['terrain'] and (random.random() <= 0.75 and faction in monster['faction'])
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

    method = random.choices(
        [1, 2, 3, 4], 
        [0.75, 0.5 if xp_budget >= 600 else 0, 0.25 if xp_budget >= 3000 else 0, 1]
    )[0]

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

def generate_encounter_data(party_size, party_level, difficulty, terrain, faction, monsters_by_cr):
    filtered_monsters_by_cr = filter_monsters_by_terrain_and_faction(monsters_by_cr, terrain, faction)
    
    if difficulty == "random":
        difficulty = random.choices(["easy", "medium", "hard", "deadly"], [0.14, 0.68, 0.13, 0.05])[0]

    xp_budget = get_party_xp_threshold(party_size, party_level, difficulty)
    encounter = generate_encounter(xp_budget, filtered_monsters_by_cr)

    encounter_distance = generate_encounter_distance(terrain)

    return {
        "encounter": encounter,
        "difficulty": difficulty,
        "xp_budget": xp_budget,
        "encounter_distance": encounter_distance,
    }

def save_encounter_data(encounter_data, file_path):
    with open(file_path, 'w') as f:
        json.dump(encounter_data, f, indent=4)

if __name__ == "__main__":
    party_size = 4
    party_level = 3
    difficulty = "medium"
    terrain = "forest"
    faction = "Wildthings"

    encounter_data = generate_encounter_data(party_size, party_level, difficulty, terrain, faction, monsters_by_cr)
    save_encounter_data(encounter_data, 'encounter_data.json')
    print(f"Encounter data saved to 'encounter_data.json'")
