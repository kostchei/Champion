# creator.py

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

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def calculate_stat_modifier(score):
    stat_bonus = load_json('./utils/stat_bonus.json')["stat_bonus"]
    for bonus in stat_bonus:
        if '-' in bonus["score_range"]:
            min_score, max_score = map(int, bonus["score_range"].split('-'))
            if min_score <= score <= max_score:
                return bonus["modifier"]
        elif int(bonus["score_range"]) == score:
            return bonus["modifier"]
    return 0

def get_proficiency_bonus(experience_points):
    experience_table = load_json('./utils/experience.json')["experience"]
    for entry in experience_table:
        if experience_points < entry["experience_points"]:
            return previous_entry["proficiency_bonus"], previous_entry["level"]
        previous_entry = entry
    return experience_table[-1]["proficiency_bonus"], experience_table[-1]["level"]

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

def choose_fighter_equipment(character_data):
    dexterity = character_data["dexterity"]
    class_details = get_class_details(character_data["class"])
    
    if dexterity <= 11:
        equipment = class_details["class_equipment"]["options"]["Heavy"]
    elif 12 <= dexterity <= 15:
        equipment = class_details["class_equipment"]["options"]["Medium"]
    else:
        equipment = class_details["class_equipment"]["options"]["Light"]
    
    return equipment

def calculate_hit_points(character_data, class_details):
    level = character_data["level"]
    constitution_modifier = character_data["constitution_modifier"]
    base_hp = class_details["hit_points"]["level_1"]
    if level > 1:
        base_hp += sum(max(random.randint(1, int(class_details["hit_points"]["other_levels"]["die"][2:])), 
                           class_details["hit_points"]["other_levels"]["minimum"]) + constitution_modifier for _ in range(1, level))
    return base_hp + constitution_modifier * level

def calculate_armor_class(character_data):
    armor_data = load_json('./utils/armor.json')["armor"]
    equipped_armor = character_data.get("equipment", [])
    dex_modifier = character_data["dexterity_modifier"]
    
    ac = 10 + dex_modifier  # Default AC if no armor is found
    
    for item in equipped_armor:
        for armor in armor_data:
            if armor["name"].lower() == item.lower():
                if armor["type"] == "Light":
                    ac = armor["armor_class"] + dex_modifier
                elif armor["type"] == "Medium":
                    ac = armor["armor_class"] + min(dex_modifier, 2)
                elif armor["type"] == "Heavy":
                    ac = armor["armor_class"]
                if "shield" in item.lower():
                    ac += 2
                break
    
    return ac

def finalize_character(character_data):
    # Get detailed class information
    class_details = get_class_details(character_data["class"])
    character_data.update({
        "class_features": class_details.get("features", {}),
        "class_equipment": class_details.get("class_equipment", [])
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

    # Add class equipment
    if character_data["class"] == "Fighter":
        fighter_equipment = choose_fighter_equipment(character_data)
        character_data["equipment"] = fighter_equipment + background_details.get("equipment", [])
    else:
        character_data["equipment"] = class_details.get("class_equipment", {}).get("options", []) + background_details.get("equipment", [])

    # Calculate and store stat modifiers
    for stat in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
        character_data[f"{stat}_modifier"] = calculate_stat_modifier(character_data[stat])
    
    # Set initial level, experience points, and proficiency bonus
    character_data["experience_points"] = 0
    character_data["level"] = 1
    character_data["proficiency_bonus"] = 2

    # Calculate and store hit points
    character_data["hit_points"] = calculate_hit_points(character_data, class_details)

    # Calculate and store armor class
    character_data["armor_class"] = calculate_armor_class(character_data)

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
