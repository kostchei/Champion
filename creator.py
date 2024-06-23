import json
import sys
import random
import subprocess
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

from utils.classes import get_class_details
from utils.races import get_race_details
from utils.backgrounds import get_background_details

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'tables', 'game_database.db')
    return sqlite3.connect(db_path)

def get_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM names')
    names = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return names

def get_random_name():
    names = get_names()
    return random.choice(names)

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
    primary_stat = class_details.get('primary_stat', '').lower()
    secondary_stat = class_details.get('secondary_stat', '').lower()
    tertiary_stat = class_details.get('tertiary_stat', '').lower()
    
    # Debug prints to check values
    print("Primary Stat:", primary_stat)
    print("Secondary Stat:", secondary_stat)
    print("Tertiary Stat:", tertiary_stat)
    print("Character Data Keys:", character_data.keys())
    
    if primary_stat and primary_stat in character_data and character_data[primary_stat] < 15:
        character_data[primary_stat] = 15
    
    if secondary_stat and tertiary_stat:
        if secondary_stat in character_data and tertiary_stat in character_data:
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
    
    starting_equipment = class_details["starting_equipment"]
    
    print("Starting Equipment Type:", type(starting_equipment))  # Debug print
    print("Starting Equipment Content:", starting_equipment)  # Debug print

    if isinstance(starting_equipment, dict):
        if dexterity <= 11:
            equipment = starting_equipment["Heavy"]
        elif 12 <= dexterity <= 15:
            equipment = starting_equipment["Medium"]
        else:
            equipment = starting_equipment["Light"]
    else:
        raise TypeError("starting_equipment is not a dictionary")

    return equipment

def calculate_hit_points(character_data, class_details):
    level = character_data["level"]
    constitution_modifier = character_data["constitution_modifier"]
    base_hp = class_details["hd_faces"]
    if level > 1:
        base_hp += sum(max(random.randint(1, int(class_details["hd_faces"])), 
                           class_details["hd_faces"]) + constitution_modifier for _ in range(1, level))
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
        "class_equipment": class_details.get("starting_equipment", [])
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
        character_data["equipment"] = class_details.get("starting_equipment", {}).get("options", []) + background_details.get("equipment", [])

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

    # Insert the character into the database
    conn = sqlite3.connect('./tables/game_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO characters (
            name, gender, class, race, background, strength, intelligence, wisdom, dexterity, constitution, charisma,
            level, experience_points, proficiency_bonus, hit_points, armor_class, skillProficiencies, languageProficiencies,
            startingEquipment, entries
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        character_data['name'], character_data['gender'], character_data['class'], character_data['race'], character_data['background'],
        character_data['strength'], character_data['intelligence'], character_data['wisdom'], character_data['dexterity'],
        character_data['constitution'], character_data['charisma'], character_data['level'], character_data['experience_points'],
        character_data['proficiency_bonus'], character_data['hit_points'], character_data['armor_class'],
        json.dumps(character_data.get('skillProficiencies', [])), json.dumps(character_data.get('languageProficiencies', [])),
        json.dumps(character_data.get('startingEquipment', [])), json.dumps(character_data.get('entries', []))
    ))
    character_id = cursor.lastrowid

    # Insert the equipment into CharacterEquipment
    for item in character_data['equipment']:
        if isinstance(item, str):
            item = {"item_name": item, "weight": 0, "value": 0, "size": "", "damage": "", "range": "", "spells": "", "charges": "", "effect": "", "image": "", "description": "", "personality": "", "other_statistics": ""}
        cursor.execute('''
            INSERT INTO CharacterEquipment (
                character_id, item_name, weight, value, size, damage, range, spells, charges, effect, image, description, personality, other_statistics
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            character_id, item['item_name'], item.get('weight', 0), item.get('value', 0), item.get('size', ''),
            item.get('damage', ''), item.get('range', ''), item.get('spells', ''), item.get('charges', ''),
            item.get('effect', ''), item.get('image', ''), item.get('description', ''), item.get('personality', ''),
            item.get('other_statistics', '')
        ))

    conn.commit()
    conn.close()

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
