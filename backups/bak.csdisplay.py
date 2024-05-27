import json
import sys
import tkinter as tk
from tkinter import messagebox

def save_character(character_data):
    character_name = character_data['name']
    realm = realm_var.get()
    if not realm:
        realm = "tier_1"
    filename = f"./saves/{character_name}.{realm}.json"
    with open(filename, 'w') as f:
        json.dump(character_data, f)
    messagebox.showinfo("Saved", f"Character saved as {filename}")
    root.quit()

def display_character_sheet(character_data):
    global root, realm_var
    root = tk.Tk()
    root.title("Character Sheet")
    root.geometry("1200x1000")

    # Create a grid layout
    grid = tk.Frame(root)
    grid.pack(padx=10, pady=10)

    # Character details
    details = {
        "Character Name": character_data['name'],
        "Gender": character_data['gender'],
        "Game Edition": character_data['game_edition'],
        "Race": character_data['race'],
        "Class": character_data['class'],
        "Background": character_data['background']
    }

    for i, (label, value) in enumerate(details.items()):
        tk.Label(grid, text=f"{label}:", font=("Arial", 14)).grid(row=i, column=0, sticky="w")
        tk.Label(grid, text=value, font=("Arial", 14)).grid(row=i, column=1, sticky="w")

    # Character attributes
    attributes = {
        "Strength": character_data['strength'],
        "Dexterity": character_data['dexterity'],
        "Constitution": character_data['constitution'],
        "Intelligence": character_data['intelligence'],
        "Wisdom": character_data['wisdom'],
        "Charisma": character_data['charisma']
    }

    for i, (label, value) in enumerate(attributes.items()):
        tk.Label(grid, text=f"{label}:", font=("Arial", 14)).grid(row=i + len(details), column=0, sticky="w")
        tk.Label(grid, text=value, font=("Arial", 14)).grid(row=i + len(details), column=1, sticky="w")

    # Placeholder for other attributes
    other_attributes = [
        "Equipment", "Armour Class", "Encumberance", "XP", "Level",
        "Movement", "Total Hitpoints", "Death Saves", "Fatigue",
        "Reputation Authority", "Reputation Guild", "Reputation Faction", "Passive Intimidation",
        "Proficiency", "Inspiration", "Passive Perception"
    ]
    for i, attr in enumerate(other_attributes):
        tk.Label(grid, text=attr, font=("Arial", 14)).grid(row=i, column=2, pady=10, padx=10)
        tk.Entry(grid).grid(row=i, column=3, padx=10)

    skills = ["Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", "History"]
    for i, skill in enumerate(skills):
        tk.Label(grid, text=skill, font=("Arial", 14)).grid(row=i, column=4, pady=5, padx=10, sticky="w")
        tk.Entry(grid).grid(row=i, column=5, padx=10)

    # Realm selection
    tk.Label(grid, text="Realm:", font=("Arial", 14)).grid(row=len(details) + len(attributes), column=0, sticky="w")
    realm_var = tk.StringVar(value="tier_1")
    realm_entry = tk.Entry(grid, textvariable=realm_var, font=("Arial", 14))
    realm_entry.grid(row=len(details) + len(attributes), column=1, sticky="w")

    # OK button to save the data
    ok_button = tk.Button(root, text="OK", command=lambda: save_character(character_data))
    ok_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    input_file = sys.argv[1]
    
    with open(input_file, 'r') as f:
        character_data = json.load(f)
    
    display_character_sheet(character_data)
