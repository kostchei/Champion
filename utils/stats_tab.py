import tkinter as tk
import json
from utils.db_utils import get_stat_modifier, get_db_connection

def create_stats_frame(parent, character_stats, level, proficiency_bonus, primary_stat, secondary_stat, character_id):
    """ Create the stats frame. """
    frame = tk.Frame(parent, bg="#F7F6ED")
    
    attributes_skills = {
        "Strength": ["str_save", "athletics"], 
        "Intelligence": ["int_save", "arcana", "history", "investigation", "nature", "religion"],
        "Wisdom": ["wis_save", "animal handling", "insight", "medicine", "perception", "survival"], 
        "Dexterity": ["dex_save", "acrobatics", "sleight of hand", "stealth"],
        "Constitution": ["con_save"], 
        "Charisma": ["cha_save", "deception", "intimidation", "performance", "persuasion"]
    }

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch skills and saves for the character
    cursor.execute('SELECT skillProficiencies, saves FROM characters WHERE id = ?', (character_id,))
    character_data = cursor.fetchone()
    
    skill_proficiencies = json.loads(character_data['skillProficiencies'])
    saves_proficiencies = json.loads(character_data['saves'])
    
    conn.close()

    row_offset = 0
    for attribute, skills_and_saves in attributes_skills.items():
        attribute_value = character_stats[attribute]
        attribute_modifier = character_stats[f"{attribute}_modifier"]
        tk.Label(frame, text=f"{attribute}:", font=("Arial", 14), bg="#F7F6ED", fg="#1E2832").grid(row=row_offset, column=0, sticky="w", padx=10, pady=5)
        tk.Label(frame, text=f"{attribute_value} ({attribute_modifier:+})", font=("Arial", 14), bg="#F7F6ED", fg="#1E2832").grid(row=row_offset, column=1, sticky="w", padx=10, pady=5)
        row_offset += 1
        for skill_or_save in skills_and_saves:
            if "save" in skill_or_save:
                proficiency = proficiency_bonus if attribute in saves_proficiencies else 0
            else:
                proficiency = proficiency_bonus if skill_or_save.replace("_", " ") in skill_proficiencies else 0
            bonus = attribute_modifier + proficiency
            bullet = "●" if proficiency else "○"
            tk.Label(frame, text=f"{bullet} {skill_or_save.replace('_', ' ').title()} ({bonus:+})", font=("Arial", 14), bg="#F7F6ED", fg="#1E2832").grid(row=row_offset, column=1, sticky="w", padx=10, pady=2)
            row_offset += 1

    tk.Label(frame, text=f"Level: {level}", font=("Arial", 14), bg="#F7F6ED", fg="#1E2832").grid(row=row_offset, column=0, sticky="w", padx=10, pady=5)
    tk.Label(frame, text=f"Proficiency Bonus: {proficiency_bonus:+}", font=("Arial", 14), bg="#F7F6ED", fg="#1E2832").grid(row=row_offset, column=1, sticky="w", padx=10, pady=5)

    frame.pack(fill=tk.BOTH, expand=True)
    return frame