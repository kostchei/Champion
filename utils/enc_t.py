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

def get_cr_for_xp(db_path, xp_limit):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT cr, xp FROM xp4cr WHERE xp <= ? ORDER BY xp DESC", (xp_limit,))
    cr = cursor.fetchone()
    conn.close()
    return cr[0] if cr else "0"

def method_solo(db_path, encounter_budget):
    reduced_budget = encounter_budget / 1.5
    cr = get_cr_for_xp(db_path, reduced_budget)
    return {"CRs": [cr]}

def method_ii(db_path, encounter_budget):
    reduced_budget = encounter_budget / 4
    cr = get_cr_for_xp(db_path, reduced_budget)
    return {"CRs": [cr, cr]}

def method_iii(db_path, encounter_budget):
    reduced_budget = encounter_budget / 7.5
    cr = get_cr_for_xp(db_path, reduced_budget)
    return {"CRs": [cr, cr, cr]}

def method_iv(db_path, encounter_budget):
    reduced_budget = encounter_budget / 2
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT cr, xp FROM xp4cr WHERE xp <= ? ORDER BY xp DESC", (reduced_budget,))
    cr1 = cursor.fetchone()
    if cr1:
        cr1_id = cursor.execute("SELECT id FROM xp4cr WHERE cr = ?", (cr1[0],)).fetchone()[0]
        cursor.execute("SELECT cr, xp FROM xp4cr WHERE xp <= ? AND id != ? AND id IN (?, ?) ORDER BY xp DESC", 
                       (reduced_budget - cr1[1], cr1_id, cr1_id - 1, cr1_id + 1))
        cr2 = cursor.fetchone()
        if cr2:
            conn.close()
            return {"CRs": [cr1[0], cr2[0]]}
        else:
            cursor.execute("SELECT cr FROM xp4cr WHERE xp <= ? AND id != ? ORDER BY xp DESC LIMIT 1", 
                           (reduced_budget - cr1[1], cr1_id))
            cr2 = cursor.fetchone()
            conn.close()
            if cr2:
                return {"CRs": [cr1[0], cr2[0]]}
    conn.close()
    return {"CRs": ["0", "1/8"]}

def method_v(db_path, encounter_budget):
    reduced_budget = encounter_budget / 3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT cr, xp FROM xp4cr WHERE xp <= ? ORDER BY xp DESC", (reduced_budget,))
    cr1 = cursor.fetchone()
    if cr1:
        cr1_id = cursor.execute("SELECT id FROM xp4cr WHERE cr = ?", (cr1[0],)).fetchone()[0]
        cursor.execute("SELECT cr, xp FROM xp4cr WHERE xp <= ? AND id != ? AND id IN (?, ?) ORDER BY xp DESC", 
                       (reduced_budget - cr1[1], cr1_id, cr1_id - 1, cr1_id + 1))
        cr2 = cursor.fetchone()
        if cr2:
            conn.close()
            return {"CRs": [cr1[0], cr1[0], cr2[0]]}
        else:
            cursor.execute("SELECT cr FROM xp4cr WHERE xp <= ? AND id != ? ORDER BY xp DESC LIMIT 1", 
                           (reduced_budget - cr1[1], cr1_id))
            cr2 = cursor.fetchone()
            conn.close()
            if cr2:
                return {"CRs": [cr1[0], cr1[0], cr2[0]]}
    conn.close()
    return {"CRs": ["0", "0", "1/8"]}

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
    
    if method == "solo":
        result = method_solo(db_path, encounter_budget)
    elif method == "method_ii":
        result = method_ii(db_path, encounter_budget)
    elif method == "method_iii":
        result = method_iii(db_path, encounter_budget)
    elif method == "method_iv":
        result = method_iv(db_path, encounter_budget)
    elif method == "method_v":
        result = method_v(db_path, encounter_budget)
    
    encounter_info = {
        "character_id": character_id,
        "character_level": character_level,
        "difficulty": difficulty,
        "encounter_budget": encounter_budget,
        "method": method,
        "CRs": result["CRs"]
    }
    
    return encounter_info

# Example usage
if __name__ == "__main__":
    DB_PATH = get_resource_path(os.path.join('..', 'tables', 'game_database.db'))
    encounter_info = encounter_script(DB_PATH)
    print(encounter_info)
