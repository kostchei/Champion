import json

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON from {file_path}: {e}")
        return None

def fix_monster_structure(monsters):
    for monster in monsters:
        # Ensure 'cr' is present and is a string
        if 'cr' not in monster or not isinstance(monster['cr'], str):
            monster['cr'] = "N/A"  # or some default value

def save_json(file_path, data):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving JSON to {file_path}: {e}")

# Load JSON files
dungeon_t1 = load_json('/mnt/data/dungeon_t1.json')
hesperia = load_json('/mnt/data/hesperia.json')

# Fix structures if loaded successfully
if dungeon_t1:
    fix_monster_structure(dungeon_t1.get('monster', []))
    save_json('/mnt/data/dungeon_t1_fixed.json', dungeon_t1)

if hesperia:
    fix_monster_structure(hesperia.get('monster', []))
    save_json('/mnt/data/hesperia_fixed.json', hesperia)

print("JSON files have been checked and fixed if necessary.")
