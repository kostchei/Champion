import tkinter as tk
from utils.db_utils import get_stat_modifier, get_skill_bonus

def create_stats_frame(parent, character_stats, level, proficiency_bonus, primary_stat, secondary_stat):
    """ Create the stats frame. """
    frame = tk.Frame(parent, bg="#F7F6ED")
    
    attributes_skills = {
        "Strength": ["Str Save", "Athletics"], 
        "Intelligence": ["Int Save", "Arcana", "History", "Investigation", "Nature", "Religion"],
        "Wisdom": ["Wis Save", "Animal Handling", "Insight", "Medicine", "Perception", "Survival"], 
        "Dexterity": ["Dex Save", "Acrobatics", "Sleight of Hand", "Stealth"],
        "Constitution": ["Con Save"], 
        "Charisma": ["Cha Save", "Deception", "Intimidation", "Performance", "Persuasion"]
    }

    row_offset = 0
    for attribute, skills in attributes_skills.items():
        attribute_value = character_stats[attribute]
        attribute_modifier = character_stats[f"{attribute}_modifier"]
        tk.Label(frame, text=f"{attribute}:", font=("Arial", 12), bg="#F7F6ED", fg="#1E2832").grid(row=row_offset, column=0, sticky="w", padx=10, pady=5)
        tk.Label(frame, text=f"{attribute_value} ({attribute_modifier:+})", font=("Arial", 12), bg="#F7F6ED", fg="#1E2832").grid(row=row_offset, column=1, sticky="w", padx=10, pady=5)
        row_offset += 1
        for skill in skills:
            skill_key = skill.lower().replace(" ", "_")
            bullet = "●" if skill in set(character_stats.get("skills", [])).union(set(character_stats.get("class_skills", []))) else "○"
            skill_bonus = get_skill_bonus(skill_key, attribute_modifier, proficiency_bonus, primary_stat, secondary_stat)
            tk.Label(frame, text=f"{bullet} {skill} ({skill_bonus:+})", font=("Arial", 12), bg="#F7F6ED", fg="#1E2832").grid(row=row_offset, column=1, sticky="w", padx=10, pady=2)
            row_offset += 1

    tk.Label(frame, text=f"Level: {level}", font=("Arial", 12), bg="#F7F6ED", fg="#1E2832").grid(row=row_offset, column=0, sticky="w", padx=10, pady=5)
    tk.Label(frame, text=f"Proficiency Bonus: {proficiency_bonus:+}", font=("Arial", 12), bg="#F7F6ED", fg="#1E2832").grid(row=row_offset, column=1, sticky="w", padx=10, pady=5)

    frame.pack(fill=tk.BOTH, expand=True)
    return frame

def get_skill_bonus(skill_key, attribute_modifier, proficiency_bonus, primary_stat, secondary_stat):
    """ Calculate the skill bonus. """
    if skill_key in primary_stat or skill_key in secondary_stat:
        return attribute_modifier + proficiency_bonus
    return attribute_modifier
