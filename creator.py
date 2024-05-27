import json
import sys
import random
import subprocess

def generate_character_stats(character_data):
    def roll_dice():
        # Roll 4 six-sided dice and take the sum of the highest 3
        rolls = [random.randint(1, 6) for _ in range(4)]
        return sum(sorted(rolls, reverse=True)[:3])
    
    while True:
        # Update stats in the character_data dictionary
        character_data['strength'] = roll_dice()
        character_data['intelligence'] = roll_dice()
        character_data['wisdom'] = roll_dice()
        character_data['dexterity'] = roll_dice()
        character_data['constitution'] = roll_dice()
        character_data['charisma'] = roll_dice()
        
        # Calculate the total sum of the stats
        total_stats = sum(character_data[key] for key in ['strength', 'intelligence', 'wisdom', 'dexterity', 'constitution', 'charisma'])
        
        # Check if the total stats are at least 75, otherwise reroll
        if total_stats >= 75:
            return character_data

if __name__ == "__main__":
    input_file = sys.argv[1]

    with open(input_file, 'r') as f:
        character_data = json.load(f)
    
    character_data = generate_character_stats(character_data)  # Generate new stats

    with open(input_file, 'w') as f:
        json.dump(character_data, f, indent=4)  # Save the new stats in a formatted way

    # Call the csdisplay.py script
    subprocess.run(['python', 'csdisplay.py', input_file])
