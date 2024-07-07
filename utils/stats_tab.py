import tkinter as tk
from utils.db_utils import get_stat_modifier, get_skill_bonus, get_db_connection

def create_stats_frame(parent, character_stats, level, proficiency_bonus, primary_stat, secondary_stat, character_id):
    """ Create the stats frame. """
    frame = tk.Frame(parent, bg="#F7F6ED")
    
    attributes_skills = {
        "Strength": ["str_save", "athletics"], 
        "Intelligence": ["int_save", "arcana", "history", "investigation", "nature", "religion"],
        "Wisdom": ["wis_save", "animal_handling", "insight", "medicine", "perception", "survival"], 
        "Dexterity": ["dex_save", "acrobatics", "sleight_of_hand", "stealth"],
        "Constitution": ["con_save"], 
        "Charisma": ["cha_save", "deception", "intimidation", "performance", "persuasion"]
    }

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch skills and saves for the character
    cursor.execute('SELECT skill, value FROM character_skills WHERE character_id = ?', (character_id,))
    skills = dict(cursor.fetchall())
    
    cursor.execute('SELECT save, value FROM character_saves WHERE character_id = ?', (character_id,))
    saves = dict(cursor.fetchall())
    
    conn.close()

    row_offset = 0
    for attribute, skills_and_saves in attributes_skills.items():
        attribute_value = character_stats[attribute]
        attribute_modifier = character_stats[f"{attribute}_modifier"]
        tk.Label(frame, text=f"{attribute}:", font=("Arial", 14), bg="#F7F6ED", fg="#1E2832").grid(row=row_offset, column=0, sticky="w", padx=10, pady=5)
        tk.Label(frame, text=f"{attribute_value} ({attribute_modifier:+})", font=("Arial", 14), bg="#F7F6ED", fg="#1E2832").grid(row=row_offset, column=1, sticky="w", padx=10, pady=5)
        row_offset += 1
        for skill_or_save in skills_and_saves:
            bullet = "●" if skill_or_save in character_stats.get("class_skills", []) else "○"
            skill_bonus = skills.get(skill_or_save, 0)
            save_bonus = saves.get(skill_or_save, 0)
            bonus = skill_bonus if "save" not in skill_or_save else save_bonus
            tk.Label(frame, text=f"{bullet} {skill_or_save.replace('_', ' ').title()} ({bonus:+})", font=("Arial", 14), bg="#F7F6ED", fg="#1E2832").grid(row=row_offset, column=1, sticky="w", padx=10, pady=2)
            row_offset += 1

    tk.Label(frame, text=f"Level: {level}", font=("Arial", 14), bg="#F7F6ED", fg="#1E2832").grid(row=row_offset, column=0, sticky="w", padx=10, pady=5)
    tk.Label(frame, text=f"Proficiency Bonus: {proficiency_bonus:+}", font=("Arial", 14), bg="#F7F6ED", fg="#1E2832").grid(row=row_offset, column=1, sticky="w", padx=10, pady=5)

    frame.pack(fill=tk.BOTH, expand=True)
    return frame
