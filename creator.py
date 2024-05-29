import json
import sys
import random
import subprocess
import os
import tkinter as tk
from tkinter import ttk, messagebox

from utils.classes import get_class_details  # Import the function from classes.py
from utils.races import get_race_details  # Import the function from races.py
from utils.backgrounds import get_background_details  # Import the function from backgrounds.py

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

class StatSelectionDialog(tk.Toplevel):
    def __init__(self, parent, options):
        super().__init__(parent)
        self.title("Choose a Stat")
        self.geometry("300x100")
        self.resizable(False, False)

        self.var = tk.StringVar(self)
        self.var.set(options[0])

        label = tk.Label(self, text="Choose a stat to increase by 2:")
        label.pack(pady=10)

        self.dropdown = ttk.Combobox(self, textvariable=self.var, values=options)
        self.dropdown.pack(pady=5)

        button = tk.Button(self, text="OK", command=self.on_select)
        button.pack(pady=5)

    def on_select(self):
        self.selected_option = self.var.get()
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.wait_window()
        return getattr(self, "selected_option", None)

def apply_class_requirements(character_data, class_details):
    primary_stat = class_details['attributes']['primary'].lower()
    secondary_stat = class_details['attributes']['secondary'].lower()
    tertiary_stat = class_details['attributes']['tertiary'].lower()
    
    if character_data[primary_stat] < 15:
        character_data[primary_stat] = 15
    
    if character_data[secondary_stat] < 13 and character_data[tertiary_stat] < 13:
        character_data[secondary_stat] = 13

def apply_race_bonuses(character_data, race_details):
    if "ability_score_increase" in race_details:
        bonus_type = race_details['ability_score_increase']['type']
        if bonus_type == "fixed":
            for stat, value in race_details['ability_score_increase']['values'].items():
                character_data[stat.lower()] += value
        elif bonus_type == "choice":
            root = tk.Tk()
            root.withdraw()  # Hide the root window

            options = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
            dialog = StatSelectionDialog(root, options)
            stat_choice = dialog.show()

            if stat_choice in options:
                character_data[stat_choice.lower()] += 2
            else:
                messagebox.showerror("Invalid Choice", "You must choose a valid stat.")
                root.quit()
            root.destroy()

def finalize_character(character_data):
    # Get detailed class information
    class_details = get_class_details(character_data["class"])
    character_data.update({
        "class_features": class_details.get("features", {}),
        "class_equipment": class_details.get("equipment", [])
    })
    
    # Apply class requirements
    apply_class_requirements(character_data, class_details)

    # Get detailed race information
    race_details = get_race_details(character_data["race"])
    character_data.update(race_details)
    
    # Apply race bonuses
    apply_race_bonuses(character_data, race_details)

    # Get detailed background information
    background_details = get_background_details(character_data["background"])
    character_data.update({
        "background_features": background_details.get("features", []),
        "background_equipment": background_details.get("equipment", [])
    })

    if not os.path.exists('./saves'):
        os.makedirs('./saves')
    with open('./saves/character.json', 'w') as f:
        json.dump(character_data, f)

if __name__ == "__main__":
    input_file = sys.argv[1]

    with open(input_file, 'r') as f:
        character_data = json.load(f)

    character_data["name"] = character_data.get("name") or get_random_name()  # Ensure name is always randomized
    character_data["gender"] = character_data.get("gender")
    character_data["game_edition"] = character_data.get("game_edition")
    character_data["race"] = character_data.get("race")
    character_data["class"] = character_data.get("class")
    character_data["background"] = character_data.get("background")
    
    character_data = generate_character_stats(character_data)  # Generate new stats
    finalize_character(character_data)  # Finalize the character details

    with open(input_file, 'w') as f:
        json.dump(character_data, f, indent=4)  # Save the new stats in a formatted way

    # Call the csdisplay.py script
    subprocess.run(['python', 'csdisplay.py', input_file])
