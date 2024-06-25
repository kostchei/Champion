import json
import sys
import random
import subprocess
import os
import sqlite3
from contextlib import closing
import tkinter as tk
from tkinter import ttk, messagebox
import logging

from utils.classes import get_class_details
from utils.races import get_race_details
from utils.backgrounds import get_background_details

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set the correct path for the database
DB_PATH = os.path.join(os.path.dirname(__file__), 'tables', 'game_database.db')

def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def execute_db_query(query, params=None, fetch=True):
    """Execute a database query and optionally fetch results."""
    try:
        with closing(get_db_connection()) as conn:
            if conn is None:
                return None
            with closing(conn.cursor()) as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                if fetch:
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Database error occurred: {e}")
        return None

def load_temporary_character(temp_character_id):
    """Load temporary character data from the database."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('SELECT * FROM temporary_characters WHERE id = ?', (temp_character_id,))
            character_data = cursor.fetchone()
    
    if character_data:
        return {
            "name": character_data[1],
            "gender": character_data[2],
            "game_editions": json.loads(character_data[3]),
            "race": character_data[4],
            "class": character_data[5],
            "background": character_data[6]
        }
    else:
        raise ValueError("Temporary character not found")

def get_names():
    """Fetch all names from the database."""
    query = 'SELECT name FROM names'
    results = execute_db_query(query)
    return [row[0] for row in results] if results else []

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
    primary_stat = class_details.get('primary_stat', '')
    secondary_stat = class_details.get('secondary_stat', '')
    tertiary_stat = class_details.get('tertiary_stat', '')
    
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
                try:
                    character_data[stat] += value
                except KeyError:
                    logger.error(f"Invalid stat key: {stat}")
        elif bonus_type == "choice":
            root = tk.Tk()
            root.withdraw()  # Hide the root window

            options = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
            dialog = StatSelectionDialog(root, options)
            stat_choice = dialog.show()

            if stat_choice in options:
                character_data[stat_choice] += 2
            else:
                messagebox.showerror("Invalid Choice", "You must choose a valid stat.")
                root.quit()
            root.destroy()

def choose_fighter_equipment(character_data):
    dexterity = character_data["dexterity"]
    class_details = get_class_details(character_data["class"])
    
    starting_equipment = class_details["starting_equipment"]

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
            if armor["name"] == item:
                if armor["type"] == "Light":
                    ac = armor["armor_class"] + dex_modifier
                elif armor["type"] == "Medium":
                    ac = armor["armor_class"] + min(dex_modifier, 2)
                elif armor["type"] == "Heavy":
                    ac = armor["armor_class"]
                if "shield" in item:
                    ac += 2
                break
    
    return ac

def save_final_character(character_data, temp_character_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            logger.debug(f"Saving final character: {character_data}")
            try:
                cursor.execute('''
                    INSERT INTO characters (
                        name, gender, class, race, background, strength, intelligence, wisdom, 
                        dexterity, constitution, charisma, level, experience_points, 
                        proficiency_bonus, hit_points, armor_class, skillProficiencies, 
                        languageProficiencies, startingEquipment, entries
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    character_data['name'], character_data['gender'], character_data['class'],
                    character_data['race'], character_data['background'], character_data['strength'],
                    character_data['intelligence'], character_data['wisdom'], character_data['dexterity'],
                    character_data['constitution'], character_data['charisma'], character_data['level'],
                    character_data['experience_points'], character_data['proficiency_bonus'],
                    character_data['hit_points'], character_data['armor_class'],
                    json.dumps(character_data.get('skillProficiencies', [])),
                    json.dumps(character_data.get('languageProficiencies', [])),
                    json.dumps(character_data.get('startingEquipment', [])),
                    json.dumps(character_data.get('entries', []))
                ))
                character_id = cursor.lastrowid
                logger.debug(f"Final character ID: {character_id}")

                # Insert equipment
                if character_data['equipment'] is not None:
                    for item in character_data['equipment']:
                        cursor.execute('''
                            INSERT INTO CharacterEquipment (
                                Character_ID, item_name, Weight, Value, Image, Description, Personality, Other_Statistics
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            character_id, item, 0, 0, '', '', '', ''
                        ))

                # Delete temporary character
                cursor.execute('DELETE FROM temporary_characters WHERE id = ?', (temp_character_id,))
                conn.commit()
                logger.debug("Character data saved to database and temporary character deleted.")
            except sqlite3.Error as e:
                logger.error(f"Database error while saving final character: {e}")
                conn.rollback()
                raise

def finalize_character(character_data):
    logger.debug(f"Finalizing character: {character_data}")
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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python creator.py <temp_character_id>")
        sys.exit(1)

    temp_character_id = int(sys.argv[1])
    try:
        character_data = load_temporary_character(temp_character_id)
        if character_data:
            logger.info(f"Processing character: {character_data['name']}")
            logger.debug(f"Initial character data: {character_data}")

            # Ensure all required keys are present in character_data
            required_keys = ['strength', 'intelligence', 'wisdom', 'dexterity', 'constitution', 'charisma', 'equipment']
            for key in required_keys:
                if key not in character_data:
                    character_data[key] = None

            # Generate character stats and finalize character
            character_data = generate_character_stats(character_data)
            logger.debug(f"Character data after generating stats: {character_data}")

            finalize_character(character_data)
            logger.debug(f"Character data after finalizing: {character_data}")

            save_final_character(character_data, temp_character_id)
            logger.debug(f"Character data saved to database")

            # Optionally call the display script or any other next steps
            subprocess.run(['python', 'csdisplay.py', str(character_data['id'])])
        else:
            logger.error("Failed to load temporary character data.")
            sys.exit(1)
    except ValueError as e:
        logger.error(e)
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
