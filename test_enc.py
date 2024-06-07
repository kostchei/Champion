import random
import json

# Load your data
with open('monstersByCR.json') as f:
    monsters_by_cr = json.load(f)

with open('featuresList.json') as f:
    features_list_data = json.load(f)

# Constants
terrain_distance_map = {
    'desert': lambda: roll_dice(6, 6) * 10,
    'arctic': lambda: roll_dice(6, 6) * 10,
    'forest': lambda: roll_dice(2, 8) * 10,
    'hills': lambda: roll_dice(2, 10) * 10,
    'mountains': lambda: roll_dice(4, 10) * 10,
    'jungle': lambda: roll_dice(2, 6) * 10,
}

difficulty_thresholds = [
    {"level": 1, "easy": 25, "medium": 50, "hard": 75, "deadly": 100},
    # Add remaining levels...
]

challenge_rating_list = [
    {"cr": "0", "xp": 10},
    {"cr": "1/8", "xp": 25},
    {"cr": "1/4", "xp": 50},
    {"cr": "1/2", "xp": 100},
    {"cr": "1", "xp": 200},
    # Add remaining challenge ratings...
]

features_list = features_list_data['featuresList']

# Functions
def roll_dice(number, sides):
    return sum(random.randint(1, sides) for _ in range(number))

def generate_random_feature(encounter_distance):
    random_feature = random.choice(features_list)
    distance_modifier = random.uniform(-0.5, 1.5)
    distance = encounter_distance * distance_modifier
    
    size_modifier = random.uniform(0.05, 2)
    area = encounter_distance * size_modifier
    if 'areaModifier' in random_feature:
        area *= random_feature['areaModifier']
    
    height_modifier = random_feature.get('heightModifier', 1)
    height_fraction = random.uniform(0.1, 1)
    height = encounter_distance * height_fraction * height_modifier
    
    return {
        **random_feature,
        'distance': round(distance),
        'area': round(area),
        'height': round(height),
    }

def generate_encounter_distance(terrain):
    return terrain_distance_map.get(terrain, lambda: 0)()

def generate_wind():
    roll = roll_dice(1, 20)
    if roll <= 12:
        return 'no wind'
    if roll <= 17:
        return 'light wind'
    return 'strong wind (Disadvantage on ranged, ¾ cover at long range)'

def generate_precipitation():
    roll = roll_dice(1, 20)
    if roll <= 12:
        return 'none'
    if roll <= 17:
        return 'light rain or snow (½ Cover over 100ft)'
    return 'strong rain or snow (¾ cover over 100ft)'

def generate_light_level():
    roll = roll_dice(1, 11)
    light_levels = [
        'Dawn, dim', 'Dawn, bright', 'Morning, overcast', 'Morning, clear unless precipitation',
        'Midday or night if travelling at night', 'Afternoon, overcast', 'Afternoon clear unless precipitation',
        'Dusk, bright', 'Dusk, dim', 'Night, moonlight', 'Night, dark'
    ]
    return light_levels[roll - 1]

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

def find_highest_cr(xp_budget, challenge_rating_list, filtered_monsters_by_cr):
    for cr_info in reversed(challenge_rating_list):
        if cr_info['xp'] <= xp_budget and cr_info['cr'] in filtered_monsters_by_cr:
            return cr_info['cr']
    return 0

def generate_encounter(xp_budget, challenge_rating_list, filtered_monsters_by_cr):
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
        cr = find_highest_cr(xp_budget, challenge_rating_list, filtered_monsters_by_cr)
        if cr in filtered_monsters_by_cr:
            selected_monster = random.choice(filtered_monsters_by_cr[cr])
            add_to_encounter(selected_monster, cr)
            xp_budget *= random.uniform(0.5, 1)

    elif method == 2:
        pair_budget = xp_budget / 3
        for _ in range(2):
            cr = find_highest_cr(pair_budget, challenge_rating_list, filtered_monsters_by_cr)
            if cr in filtered_monsters_by_cr:
                selected_monster = random.choice(filtered_monsters_by_cr[cr])
                add_to_encounter(selected_monster, cr)

    elif method == 3:
        minion_budget = xp_budget / 12
        for _ in range(2):
            cr = find_highest_cr(minion_budget, challenge_rating_list, filtered_monsters_by_cr)
            if cr in filtered_monsters_by_cr:
                selected_monster = random.choice(filtered_monsters_by_cr[cr])
                for _ in range(random.randint(1, 6)):
                    add_to_encounter(selected_monster, cr)

    elif method == 4:
        swarm_budget = xp_budget / 60
        for _ in range(3):
            cr = find_highest_cr(swarm_budget, challenge_rating_list, filtered_monsters_by_cr)
            if cr in filtered_monsters_by_cr:
                selected_monster = random.choice(filtered_monsters_by_cr[cr])
                for _ in range(random.randint(1, 10)):
                    add_to_encounter(selected_monster, cr)

    return encounter

def get_party_xp_threshold(party_size, party_level, difficulty_thresholds, difficulty):
    return next(threshold[difficulty] for threshold in difficulty_thresholds if threshold['level'] == party_level) * party_size

# Main function for generating encounters
def generate_encounter_data(party_size, party_level, difficulty, terrain, faction):
    filtered_monsters_by_cr = filter_monsters_by_terrain_and_faction(monsters_by_cr, terrain, faction)
    
    if difficulty == "random":
        difficulty = random.choices(["easy", "medium", "hard", "deadly"], [0.14, 0.68, 0.13, 0.05])[0]

    xp_budget = get_party_xp_threshold(party_size, party_level, difficulty_thresholds, difficulty)
    encounter = generate_encounter(xp_budget, challenge_rating_list, filtered_monsters_by_cr)

    encounter_distance = generate_encounter_distance(terrain)
    generated_features = [generate_random_feature(encounter_distance) for _ in range(3)]

    return {
        "encounter": encounter,
        "difficulty": difficulty,
        "xp_budget": xp_budget,
        "encounter_distance": encounter_distance,
        "wind": generate_wind(),
        "precipitation": generate_precipitation(),
        "light_level": generate_light_level(),
        "generated_features": generated_features,
    }

# Example usage
party_size = 2
party_level = 1
difficulty = "random"
terrain = "forest"
faction = "Elvish"

encounter_data = generate_encounter_data(party_size, party_level, difficulty, terrain, faction)
print(encounter_data)
