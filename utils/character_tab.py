import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
import os
import sys
from contextlib import closing

def get_resource_path(relative_path):
    """ Get the absolute path to the resource, works for both development and PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Set the correct path for the database
DB_PATH = get_resource_path(os.path.join('tables', 'game_database.db'))

ALL_SKILLS = [
    "acrobatics", "animal handling", "arcana", "athletics", "deception",
    "history", "insight", "intimidation", "investigation", "medicine",
    "nature", "perception", "performance", "persuasion", "religion",
    "sleight of hand", "stealth", "survival"
]

def fetch_skill_options(skill_data):
    """ Fetch skill options based on the provided skill data. """
    if isinstance(skill_data, list) and len(skill_data) > 0:
        if isinstance(skill_data[0], dict) and "any" in skill_data[0]:
            return ALL_SKILLS  # Return the full list of skills
        elif isinstance(skill_data[0], str):
            return skill_data  # Return the list as is if it's already in string format
        else:
            # Extract keys from the list of dictionaries
            return [skill for skill_dict in skill_data for skill in skill_dict]
    return []

def create_skill_selection(parent, available_skills, chosen_skills, count, callback):
    """ Create a skill selection UI. """
    frame = tk.Frame(parent, bg="#F7F6ED")
    tk.Label(frame, text=f"Choose {count} skills:", font=("Arial", 12), bg="#F7F6ED").pack(pady=5)
    skill_vars = {skill: tk.BooleanVar(value=(skill in chosen_skills)) for skill in available_skills}

    for skill, var in skill_vars.items():
        cb = tk.Checkbutton(frame, text=skill, variable=var, bg="#F7F6ED", font=("Arial", 12))
        cb.pack(anchor="w")

    def on_submit():
        selected_skills = [skill for skill, var in skill_vars.items() if var.get()]
        if len(selected_skills) == count:
            callback(selected_skills)
            frame.destroy()
        else:
            messagebox.showerror("Error", f"You must select exactly {count} skills.")
    
    tk.Button(frame, text="Submit", command=on_submit, bg="#C8C8B4", fg="#1E2832", font=("Arial", 12)).pack(pady=10)
    frame.pack(pady=10)

def update_character_skills(character_id, skills):
    """ Update the character's skills in the database. """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                UPDATE characters
                SET skillProficiencies = ?
                WHERE id = ?
            ''', (json.dumps(skills), character_id))
            conn.commit()

def create_character_frame(parent, character, lineage_data, background_data, class_data):
    """ Create the character frame. """
    frame = tk.Frame(parent, bg="#F7F6ED")
    
    # Lineage Choices
    tk.Label(frame, text="Lineage Choices", font=("Arial", 16), bg="#F7F6ED").pack(pady=10)
    tk.Label(frame, text=f"Ability Score Increase: {lineage_data['ability_score_increase']}", font=("Arial", 12), bg="#F7F6ED").pack(pady=5)
    tk.Label(frame, text="Languages:", font=("Arial", 12), bg="#F7F6ED").pack(pady=5)
    for language in json.loads(lineage_data['languages']):
        tk.Label(frame, text=language, font=("Arial", 12), bg="#F7F6ED").pack(pady=2)
    
    # Background Choices
    tk.Label(frame, text="Background Choices", font=("Arial", 16), bg="#F7F6ED").pack(pady=10)
    bg_skills = json.loads(background_data['skillProficiencies'])
    if isinstance(bg_skills, list) and isinstance(bg_skills[0], dict) and "any" in bg_skills[0]:
        skill_options = fetch_skill_options(bg_skills)
        create_skill_selection(frame, skill_options, character.get('skills', []), bg_skills[0]['any'], lambda skills: update_character_skills(character['id'], list(set(character.get('skills', []) + skills))))
    else:
        # Add fixed background skills to the character's skill proficiencies
        fixed_bg_skills = fetch_skill_options(bg_skills)
        character['skills'] = list(set(character.get('skills', []) + fixed_bg_skills))
        update_character_skills(character['id'], character['skills'])

    # Class Choices
    tk.Label(frame, text="Class Choices", font=("Arial", 16), bg="#F7F6ED").pack(pady=10)
    class_skills = json.loads(class_data['skill_proficiencies'])
    skill_options = fetch_skill_options(class_skills)
    create_skill_selection(frame, skill_options, character.get('class_skills', []), class_skills[0]['choose']['count'], lambda skills: update_character_skills(character['id'], list(set(character.get('skills', []) + skills))))

    frame.pack(fill=tk.BOTH, expand=True)
    return frame
