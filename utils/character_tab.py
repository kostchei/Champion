import tkinter as tk
from tkinter import ttk, messagebox
import json

def fetch_skill_options(skill_data):
    """ Fetch skill options based on the provided skill data. """
    skill_options = []
    if isinstance(skill_data, dict) and "choose" in skill_data:
        skill_options = skill_data["choose"]["from"]
    return skill_options

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
    bg_skills = json.loads(background_data['skillProficiencies'])[0]
    skill_options = fetch_skill_options(bg_skills)
    create_skill_selection(frame, skill_options, character.get('skills', []), 2, lambda skills: print("Background skills chosen:", skills))

    # Class Choices
    tk.Label(frame, text="Class Choices", font=("Arial", 16), bg="#F7F6ED").pack(pady=10)
    class_skills = json.loads(class_data['skill_proficiencies'])[0]
    skill_options = fetch_skill_options(class_skills)
    create_skill_selection(frame, skill_options, character.get('class_skills', []), class_skills['choose']['count'], lambda skills: print("Class skills chosen:", skills))

    frame.pack(fill=tk.BOTH, expand=True)
    return frame
