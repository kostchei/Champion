# csdisplay.py

import json
import sys
import tkinter as tk
from tkinter import messagebox

BUFF_OFF_WHITE = "#F7F6ED"
DARK_BLUE = "#1E2832"
WHITE = "#EDF3FC"
GREY = "#F0F0E6"

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
    root.configure(bg=BUFF_OFF_WHITE)

    # Create a canvas for scrolling
    canvas = tk.Canvas(root, bg=BUFF_OFF_WHITE)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Add a scrollbar
    scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)

    # Configure canvas scrolling
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Create a frame inside the canvas
    frame = tk.Frame(canvas, bg=BUFF_OFF_WHITE)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    # Character details
    details = [
        ("Character Name", character_data['name']),
        ("Gender", character_data['gender']),
        ("Game Edition", character_data['game_edition']),
        ("Race", character_data['race']),
        ("Class", character_data['class']),
        ("Background", character_data['background'])
    ]

    for i, (label, value) in enumerate(details):
        row = i // 3
        col = (i % 3) * 2
        tk.Label(frame, text=f"{label}:", font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row, column=col, sticky="w", padx=10, pady=5)
        tk.Label(frame, text=value, font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row, column=col + 1, sticky="w", padx=10, pady=5)

    # Character attributes and skills in the preferred order
    attributes_skills = [
        ("Strength", ["Saving Throw", "Athletics", "Armour", "AC"]),
        ("Intelligence", ["Saving Throw", "Arcana", "History", "Investigation", "Nature", "Religion"]),
        ("Wisdom", ["Saving Throw", "Animal Handling", "Insight", "Medicine", "Perception", "Survival"]),
        ("Dexterity", ["Saving Throw", "Acrobatics", "Sleight of Hand", "Stealth"]),
        ("Constitution", ["Saving Throw", "Hitpoints"]),
        ("Charisma", ["Saving Throw", "Deception", "Intimidation", "Performance", "Persuasion"])
    ]

    saving_throws = character_data.get("saving_throws", [])

    row_offset = 2
    for i, (attribute, skills) in enumerate(attributes_skills):
        # Display attribute label and value
        tk.Label(frame, text=f"{attribute}:", font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row_offset, column=0, sticky="w", padx=10, pady=5)
        tk.Label(frame, text=character_data[attribute.lower()], font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row_offset, column=1, sticky="w", padx=10, pady=5)
        row_offset += 1
        
        for j, skill in enumerate(skills):
            skill_key = skill.lower().replace(" ", "_")
            has_skill = character_data.get(skill_key, False) or skill == "Saving Throw" and attribute in saving_throws
            bullet = "●" if has_skill else "○"
            tk.Label(frame, text=f"{bullet} {skill}", font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row_offset, column=1, sticky="w", padx=10, pady=2)
            row_offset += 1

    # Realm selection
    tk.Label(frame, text="Realm:", font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row_offset, column=0, sticky="w", padx=10, pady=5)
    realm_var = tk.StringVar(value="tier_1")
    realm_entry = tk.Entry(frame, textvariable=realm_var, font=("Arial", 14), bg=WHITE, fg=DARK_BLUE)
    realm_entry.grid(row=row_offset, column=1, sticky="w", padx=10, pady=5)
    row_offset += 1

    # Create a separate frame for lists to avoid interference with skills
    list_frame = tk.Frame(frame, bg=BUFF_OFF_WHITE)
    list_frame.grid(row=0, column=4, rowspan=row_offset, sticky="n")

    # Display Features and Equipment
    def create_readonly_listbox(parent, title, items):
        tk.Label(parent, text=title, font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).pack(anchor="w", padx=10, pady=5)
        listbox = tk.Listbox(parent, height=len(items), bg=WHITE, fg=DARK_BLUE, font=("Arial", 14))
        for item in items:
            listbox.insert(tk.END, item)
        listbox.pack(anchor="w", padx=10, pady=2)
        listbox.config(state=tk.DISABLED)  # Make the listbox read-only

    create_readonly_listbox(list_frame, "Attacks", character_data.get("attacks", []))
    create_readonly_listbox(list_frame, "Features", character_data.get("class_features", []))
    create_readonly_listbox(list_frame, "Reputation", character_data.get("reputation", []))
    create_readonly_listbox(list_frame, "Equipment", character_data.get("equipment", []))

    # OK button to save the data
    ok_button = tk.Button(root, text="OK", command=lambda: save_character(character_data), bg=GREY, fg=DARK_BLUE)
    ok_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    input_file = sys.argv[1]

    with open(input_file, 'r') as f:
        character_data = json.load(f)

    display_character_sheet(character_data)
