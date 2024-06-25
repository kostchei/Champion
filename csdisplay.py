import json
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import os
import sqlite3
from contextlib import closing
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BUFF_OFF_WHITE = "#F7F6ED"
DARK_BLUE = "#1E2832"
WHITE = "#EDF3FC"
GREY = "#F0F0E6"
DB_PATH = os.path.join(os.path.dirname(__file__), 'tables', 'game_database.db')

def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def load_character(character_id):
    """Load character data from the database."""
    query_character = 'SELECT * FROM characters WHERE id = ?'
    query_equipment = 'SELECT * FROM CharacterEquipment WHERE Character_ID = ?'
    
    try:
        with closing(get_db_connection()) as conn:
            if conn is None:
                return None
            with closing(conn.cursor()) as cursor:
                cursor.execute(query_character, (character_id,))
                character_data = cursor.fetchone()

                if character_data:
                    cursor.execute(query_equipment, (character_id,))
                    equipment = [row[2] for row in cursor.fetchall()]  # assuming item_name is in the third column

                    return {
                        "id": character_data[0],
                        "name": character_data[1],
                        "gender": character_data[2],
                        "game_editions": json.loads(character_data[3]),
                        "race": character_data[4],
                        "class": character_data[5],
                        "background": character_data[6],
                        "strength": character_data[7],
                        "intelligence": character_data[8],
                        "wisdom": character_data[9],
                        "dexterity": character_data[10],
                        "constitution": character_data[11],
                        "charisma": character_data[12],
                        "level": character_data[13],
                        "experience_points": character_data[14],
                        "proficiency_bonus": character_data[15],
                        "hit_points": character_data[16],
                        "armor_class": character_data[17],
                        "skillProficiencies": json.loads(character_data[18]),
                        "languageProficiencies": json.loads(character_data[19]),
                        "startingEquipment": json.loads(character_data[20]),
                        "entries": json.loads(character_data[21]),
                        "equipment": equipment
                    }
                else:
                    raise ValueError("Character not found")
    except sqlite3.Error as e:
        logger.error(f"Database error while loading character: {e}")
        return None

def display_character_sheet(character_data):
    global root
    root = tk.Tk()
    root.title("Character Sheet")
    root.geometry("1200x1400")
    root.configure(bg=BUFF_OFF_WHITE)
    canvas = tk.Canvas(root, bg=BUFF_OFF_WHITE)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
    scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    global main_frame
    main_frame = tk.Frame(canvas, bg=BUFF_OFF_WHITE)
    canvas.create_window((0, 0), window=main_frame, anchor="nw")
    render_character_sheet(character_data)
    root.mainloop()

def render_character_sheet(character_data):
    for widget in main_frame.winfo_children():
        widget.destroy()
    details_frame = tk.Frame(main_frame, bg=BUFF_OFF_WHITE)
    details_frame.grid(row=0, column=0, columnspan=4, sticky="nsew")

    if 'current_hp' not in character_data:
        character_data['current_hp'] = character_data['hit_points']

    details = [
        ("Character Name", character_data['name']), ("Gender", character_data['gender']),
        ("Game Edition", character_data['game_editions']), ("Race", character_data['race']),
        ("Class", character_data['class']), ("Background", character_data['background']),
        ("Proficiency Bonus", character_data['proficiency_bonus']), 
        ("Experience", character_data['experience_points']), ("Level", f"Level {character_data['level']}"),
        ("Hit Points", character_data['hit_points']), 
        ("Current HP", character_data['current_hp']),
        ("Armor Class", character_data.get('armor_class', 'None'))
    ]

    for i, (label, value) in enumerate(details):
        row, col = divmod(i, 4)
        tk.Label(details_frame, text=f"{label}:", font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row, column=col*2, sticky="w", padx=10, pady=5)
        tk.Label(details_frame, text=value, font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row, column=col*2 + 1, sticky="w", padx=10, pady=5)

    main_frame.columnconfigure(0, weight=1, minsize=300)
    main_frame.columnconfigure(1, weight=1, minsize=200)
    main_frame.columnconfigure(2, weight=1, minsize=400)
    main_frame.columnconfigure(3, weight=1, minsize=200)

    attributes_frame = tk.Frame(main_frame, bg=BUFF_OFF_WHITE)
    attributes_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

    attributes_skills = {
        "Strength": ["Str Save", "Athletics"], "Intelligence": ["Int Save", "Arcana", "History", "Investigation", "Nature", "Religion"],
        "Wisdom": ["Wis Save", "Animal Handling", "Insight", "Medicine", "Perception", "Survival"], "Dexterity": ["Dex Save", "Acrobatics", "Sleight of Hand", "Stealth"],
        "Constitution": ["Con Save"], "Charisma": ["Cha Save", "Deception", "Intimidation", "Performance", "Persuasion"]
    }
    
    row_offset = 0
    for attribute, skills in attributes_skills.items():
        attribute_value = character_data[attribute.lower()]
        attribute_modifier = character_data[f"{attribute.lower()}_modifier"]
        tk.Label(attributes_frame, text=f"{attribute}:", font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row_offset, column=0, sticky="w", padx=10, pady=5)
        tk.Label(attributes_frame, text=f"{attribute_value} ({attribute_modifier:+})", font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row_offset, column=1, sticky="w", padx=10, pady=5)
        row_offset += 1
        for skill in skills:
            skill_key = skill.lower().replace(" ", "_")
            bullet = "●" if skill in set(character_data.get("skills", [])).union(set(character_data.get("class_skills", []))) else "○"
            skill_bonus = character_data.get(f"{skill_key}_bonus", 0)
            tk.Label(attributes_frame, text=f"{bullet} {skill} ({skill_bonus:+})", font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row_offset, column=1, sticky="w", padx=10, pady=2)
            row_offset += 1

    list_frame = tk.Frame(main_frame, bg=BUFF_OFF_WHITE)
    list_frame.grid(row=1, column=2, sticky="nsew")
    def create_readonly_listbox(parent, title, items):
        tk.Label(parent, text=title, font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).pack(anchor="w", padx=10, pady=5)
        listbox = tk.Listbox(parent, height=len(items), width=30, bg=WHITE, fg=DARK_BLUE, font=("Arial", 14))
        for item in items:
            listbox.insert(tk.END, item)
        listbox.pack(anchor="w", padx=10, pady=2)
        listbox.config(state=tk.DISABLED)

    attack_info = [f'{character_data["attack"]["name"]}, {character_data["attack"]["to_hit"]} to hit, {character_data["attack"]["damage"]}'] if "attack" in character_data else []
    create_readonly_listbox(list_frame, "Attack", attack_info)
    class_features = [f"{v.get('name', '')}: {v.get('description', '')}\nEffect: {v.get('effect', '')}" for k, v in character_data.items() if k.startswith("chosen_") and isinstance(v, dict)]
    create_readonly_listbox(list_frame, "Class Features", class_features)
    create_readonly_listbox(list_frame, "Reputation", character_data.get("reputation", []))
    create_readonly_listbox(list_frame, "Equipment", character_data.get("equipment", []))
    create_readonly_listbox(list_frame, "Unassigned Skills", list(set(character_data.get("skills", [])).union(set(character_data.get("class_skills", [])))))

    actions_frame = tk.Frame(main_frame, bg=BUFF_OFF_WHITE)
    actions_frame.grid(row=1, column=3, sticky="nsew")
    tk.Button(actions_frame, text="Save Changes", command=lambda: save_character(character_data), bg=GREY, fg=DARK_BLUE).pack(pady=10)

def update_character_sheet(character_data):
    render_character_sheet(character_data)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python csdisplay.py <character_id>")
        sys.exit(1)
    
    character_id = int(sys.argv[1])
    try:
        character_data = load_character(character_id)
        if character_data:
            display_character_sheet(character_data)
        else:
            logger.error("Failed to load character data.")
            sys.exit(1)
    except ValueError as e:
        logger.error(e)
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
