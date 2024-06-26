import json

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return None

def check_monster_structure(monster, file_name):
    required_keys = ['name', 'cr', 'size', 'type', 'alignment', 'ac', 'hp', 'speed', 
                     'str', 'dex', 'con', 'int', 'wis', 'cha', 'skill', 'senses', 
                     'immune', 'vulnerable', 'conditionImmune', 'trait', 'action', 
                     'reaction', 'spellcasting']
    
    missing_keys = [key for key in required_keys if key not in monster]
    
    if missing_keys:
        print(f"Monster '{monster.get('name', 'unknown')}' in '{file_name}' is missing keys: {missing_keys}")

# Load JSON files
hesperia = load_json('hesperia_fixed.json')

# Check structures
if hesperia:
    print("\nChecking 'hesperia_fixed.json' monsters...")
    for monster in hesperia.get('monster', []):
        check_monster_structure(monster, 'hesperia_fixed.json')
else:
    print("Failed to load one or both JSON files.")
