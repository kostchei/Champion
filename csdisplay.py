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

def fetch_character(character_id):
    """ Fetch character data from the database using the character ID. """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row  # This will return rows as dictionaries
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                SELECT * FROM characters WHERE id=?
            ''', (character_id,))
            return cursor.fetchone()

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

def display_character(character_id):
    character = fetch_character(character_id)
    if not character:
        logger.error(f"No character found with ID {character_id}")
        return
    
    root = tk.Tk()
    root.title(f"Character: {character['name']}")
    root.geometry("1902x1080")
    root.configure(bg=COLORS["background"])

    # Create the top frame
    create_top_frame(root, character)

    # Create a main content frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Create the notebook for tabs
    notebook = ttk.Notebook(main_frame)
    notebook.pack(side=tk.LEFT, fill=tk.Y)

    # Configure notebook to have tabs on the left
    style = ttk.Style()
    style.configure('TNotebook.Tab', padding=[10, 5], font=("Arial", 12))
    style.configure('lefttab.TNotebook', tabposition='wn')
    notebook.configure(style='lefttab.TNotebook')

    # Create a frame to display the selected tab's content
    content_frame = tk.Frame(main_frame)
    content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Create frame creation functions
    frame_creators = {
        "Character": lambda: create_character_frame(content_frame, character),
        "Inventory": lambda: create_inventory_frame(content_frame),
        "Stats": lambda: create_stats_frame(content_frame, character),
        "Log": lambda: create_log_frame(content_frame)
    }

    # Add tabs to the notebook
    for text, create_func in frame_creators.items():
        frame = tk.Frame(notebook)
        notebook.add(frame, text=text)

    def on_tab_change(event):
        # Clear the content frame
        for widget in content_frame.winfo_children():
            widget.destroy()
        
        # Get the selected tab
        selected_tab = notebook.index(notebook.select())
        # Create and display the content for the selected tab
        selected_frame = list(frame_creators.values())[selected_tab]()
        selected_frame.pack(fill=tk.BOTH, expand=True)

    notebook.bind("<<NotebookTabChanged>>", on_tab_change)

    # Trigger the tab change event for the first tab
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
