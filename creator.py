#creator.py
# add randomisation and tall the other stuff for making a 1st level character

import json
import sys

def generate_character_stats(character_data):
    # Generate stats (for example purposes)
    character_data['strength'] = 10
    character_data['dexterity'] = 12
    character_data['constitution'] = 14
    character_data['intelligence'] = 8
    character_data['wisdom'] = 10
    character_data['charisma'] = 13

    return character_data

if __name__ == "__main__":
    input_file = sys.argv[1]
    
    with open(input_file, 'r') as f:
        character_data = json.load(f)
    
    character_data = generate_character_stats(character_data)
    
    with open(input_file, 'w') as f:
        json.dump(character_data, f)
