import sqlite3
import random
import os
import sys

def get_resource_path(relative_path):
    """ Get the absolute path to the resource, works for both development and PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def get_active_character_level(db_path):
    print(f"Database path: {db_path}")  # Debugging line
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, level FROM characters WHERE active = 'true'")
    character = cursor.fetchone()
    conn.close()
    if character:
        return character[0], character[1]
    else:
        raise ValueError("No active character found.")

def get_encounter_budget(db_path, character_level, difficulty):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT {difficulty} FROM encounter_dc WHERE level = ?", (character_level,))
    budget = cursor.fetchone()
    conn.close()
    if budget:
        return budget[0]
    else:
        raise ValueError(f"No budget found for level {character_level} and difficulty {difficulty}.")

def determine_difficulty():
    roll = random.random()
    if roll < 0.20:
        return "easy"
    elif roll < 0.80:
        return "medium"
    else:
        return "hard"

def check_encounter_budget(encounter_budget):
    methods = ["solo", "method_ii", "method_iii", "method_iv", "method_v"]
    available_methods = ["solo"]

    if encounter_budget >= 50:
        available_methods.append("method_ii")
    if encounter_budget >= 75:
        available_methods.append("method_iii")
        available_methods.append("method_iv")
    if encounter_budget >= 125:
        available_methods.append("method_v")

    if "solo" in available_methods and random.random() < 0.50:
        return "solo"
    else:
        available_methods.remove("solo")
        return random.choice(available_methods) if available_methods else "solo"

def encounter_script(db_path):
    character_id, character_level = get_active_character_level(db_path)
    difficulty = determine_difficulty()
    encounter_budget = get_encounter_budget(db_path, character_level, difficulty)
    
    method = check_encounter_budget(encounter_budget)
    
    encounter_info = {
        "character_id": character_id,
        "character_level": character_level,
        "difficulty": difficulty,
        "encounter_budget": encounter_budget,
        "method": method
    }
    
    return encounter_info

# Example usage
if __name__ == "__main__":
    DB_PATH = get_resource_path(os.path.join('..', 'tables', 'game_database.db'))
    print(f"Resolved database path: {DB_PATH}")  # Debugging line
    encounter_info = encounter_script(DB_PATH)
    print(encounter_info)
