import tkinter as tk
from tkinter import ttk
import sqlite3
import json
import os
import sys
from contextlib import closing
import logging

# Import tab creation functions from utils
from utils.character_tab import create_character_frame
from utils.inventory_tab import create_inventory_frame
from utils.stats_tab import create_stats_frame
from utils.log_tab import create_log_frame
from utils.db_utils import update_character_skills, update_character_saves, get_stat_modifier, fetch_data, get_db_connection, fetch_character, fetch_level_and_proficiency_bonus, update_character_level_and_proficiency

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COLORS = {
    "button": "#F0F0E6",
    "button_hover": "#EDF3FC",
    "button_text": "#1E2832",
    "background": "#F7F6ED",
    "button_shadow": "#C8C8B4",
    "popup": "#FFFFFF",
    "popup_border": "#000000"
}

def get_resource_path(relative_path):
    """ Get the absolute path to the resource, works for both development and PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Set the correct path for the database
DB_PATH = get_resource_path(os.path.join('tables', 'game_database.db'))

def fetch_data(table, column, value):
    """ Fetch data from a specific table based on a column and value. """
    conn = get_db_connection()
    if not conn:
        return {}

    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE {column} = ?", (value,))
    data = cursor.fetchone()
    conn.close()
    return dict(data) if data else {}

def get_db_connection():
    """ Get a database connection. """
    db_path = './tables/game_database.db'
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def fetch_character(character_id):
    """ Fetch character data from the database using the character ID. """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row  # This will return rows as dictionaries
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                SELECT * FROM characters WHERE id=?
            ''', (character_id,))
            return dict(cursor.fetchone())

def fetch_level_and_proficiency_bonus(exp):
    """ Fetch the level and proficiency bonus based on experience points. """
    conn = get_db_connection()
    if not conn:
        return None, None
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT level, proficiency_bonus
        FROM xp_lv_bonus
        WHERE experience_points <= ?
        ORDER BY experience_points DESC
        LIMIT 1
    ''', (exp,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result["level"], result["proficiency_bonus"]
    else:
        return None, None

def update_character_level_and_proficiency(character_id, level, proficiency_bonus):
    """ Update the character's level and proficiency bonus in the database. """
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE characters
        SET level = ?, proficiency_bonus = ?
        WHERE id = ?
    ''', (level, proficiency_bonus, character_id))
    conn.commit()
    conn.close()

def create_top_frame(root, character):
    """ Create the top frame displaying the character's basic information. """
    top_frame = tk.Frame(root, bg=COLORS["background"])
    top_frame.pack(side=tk.TOP, fill=tk.X)

    labels = ["Name", "Gender", "Game Editions", "Race", "Class", "Background", "Exp"]
    values = [
        character['name'], character['gender'], ', '.join(json.loads(character['game_editions'])),
        character['race'], character['class'], character['background'], character['experience_points']
    ]

    for i, (label, value) in enumerate(zip(labels, values)):
        tk.Label(top_frame, text=f"{label}: {value}", font=("Arial", 12), bg=COLORS["background"]).grid(row=0, column=i, padx=5, pady=5, sticky="w")

def update_character_stats(character_id, character_stats):
    """ Update the character's stats in the database. """
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE characters
        SET strength = ?, dexterity = ?, constitution = ?, intelligence = ?, wisdom = ?, charisma = ?
        WHERE id = ?
    ''', (
        character_stats["Strength"],
        character_stats["Dexterity"],
        character_stats["Constitution"],
        character_stats["Intelligence"],
        character_stats["Wisdom"],
        character_stats["Charisma"],
        character_id
    ))
    conn.commit()
    conn.close()

def get_stat_modifier(stat_value):
    """ Fetch the modifier for a given stat value from the stat_bonus table. """
    conn = get_db_connection()
    if not conn:
        return 0
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT modifier
        FROM stat_bonus
        WHERE score = ?
    ''', (stat_value,))
    result = cursor.fetchone()
    conn.close()
    
    return result["modifier"] if result else 0

def display_character(character_id):
    character = fetch_character(character_id)
    if not character:
        logger.error(f"No character found with ID {character_id}")
        return

    exp = character['experience_points']
    level, proficiency_bonus = fetch_level_and_proficiency_bonus(exp)
    
    if level is not None and proficiency_bonus is not None:
        update_character_level_and_proficiency(character_id, level, proficiency_bonus)
        character['level'] = level
        character['proficiency_bonus'] = proficiency_bonus

    root = tk.Tk()
    root.title(f"Character: {character['name']}")
    root.geometry("1902x1080")
    root.configure(bg="#F7F6ED")

    create_top_frame(root, character)

    main_frame = tk.Frame(root, bg="#F7F6ED")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Configure the style for vertical tabs
    style = ttk.Style()
    style.theme_use('clam')  # or any other theme that supports vertical tabs
    style.configure("Vertical.TNotebook", tabposition='wn')  # 'wn' for west-north (left-top)
    style.configure("Vertical.TNotebook.Tab", width=30, padding=50, font=("Arial", 16))  # Adjust width and padding as needed

    notebook = ttk.Notebook(main_frame, style="Vertical.TNotebook")
    notebook.pack(side=tk.LEFT, fill=tk.Y)

    content_frame = tk.Frame(main_frame)
    content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    background_data = fetch_data("backgrounds", "name", character['background'])
    class_data = fetch_data("classes", "name", character['class'])
    lineage_data = fetch_data("lineages", "name", character['race'])
    
    character_stats = {
        "Strength": character['strength'],
        "Dexterity": character['dexterity'],
        "Constitution": character['constitution'],
        "Intelligence": character['intelligence'],
        "Wisdom": character['wisdom'],
        "Charisma": character['charisma'],
        "skillProficiencies": json.loads(character['skillProficiencies']),
        "saves": json.loads(character['saves']),
        "level": character['level'],
        "proficiency_bonus": character['proficiency_bonus']
    }

    # Calculate and add stat modifiers to character_stats
    for stat in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]:
        character_stats[f"{stat}_modifier"] = get_stat_modifier(character_stats[stat])

    primary_stat = class_data.get('primary_stat', '')
    secondary_stat = class_data.get('secondary_stat', '')

    frame_creators = {
        "Character": lambda: create_character_frame(content_frame, character, lineage_data, background_data, class_data),
        "Inventory": lambda: create_inventory_frame(content_frame),
        "Stats": lambda: create_stats_frame(content_frame, character_stats, character['level'], character['proficiency_bonus'], primary_stat, secondary_stat, character_id),
        "Log": lambda: create_log_frame(content_frame)
    }

    for text, create_func in frame_creators.items():
        frame = tk.Frame(notebook)
        notebook.add(frame, text=text)

    def on_tab_change(event):
        for widget in content_frame.winfo_children():
            widget.destroy()

        selected_tab = notebook.index(notebook.select())
        selected_frame = list(frame_creators.values())[selected_tab]()
        selected_frame.pack(fill=tk.BOTH, expand=True)

    notebook.bind("<<NotebookTabChanged>>", on_tab_change)

    root.after(100, lambda: notebook.event_generate("<<NotebookTabChanged>>"))

    root.mainloop()

def main(character_id):
    display_character(character_id)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python csdisplay.py <character_id>")
        sys.exit(1)

    character_id = int(sys.argv[1])
    main(character_id)
