# csdisplay.py
# this should be a nice html + css form

import json
import sys

def display_character_sheet(character_data):
    # Print character data (for example purposes)
    print(f"Name: {character_data['name']}")
    print(f"Gender: {character_data['gender']}")
    print(f"Game Edition: {character_data['game_edition']}")
    print(f"Race: {character_data['race']}")
    print(f"Class: {character_data['class']}")
    print(f"Background: {character_data['background']}")
    print(f"Strength: {character_data['strength']}")
    print(f"Dexterity: {character_data['dexterity']}")
    print(f"Constitution: {character_data['constitution']}")
    print(f"Intelligence: {character_data['intelligence']}")
    print(f"Wisdom: {character_data['wisdom']}")
    print(f"Charisma: {character_data['charisma']}")

if __name__ == "__main__":
    input_file = sys.argv[1]
    
    with open(input_file, 'r') as f:
        character_data = json.load(f)
    
    display_character_sheet(character_data)
