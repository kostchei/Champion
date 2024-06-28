import tkinter as tk
from tkinter import ttk
import json
import os
import subprocess
import random
from PIL import Image, ImageTk
from utils.names import get_random_name
from utils.game_editions import get_active_game_editions
from utils.races import get_races_for_editions
from utils.classes import get_classes
from utils.backgrounds import get_backgrounds, get_background_details
import sqlite3
from contextlib import closing
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_resource_path(relative_path):
    """ Get the absolute path to the resource, works for both development and PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Set the correct path for the database
DB_PATH = get_resource_path(os.path.join('tables', 'game_database.db'))

# Initialize the main application window
root = tk.Tk()
root.title("Character Generator")
root.configure(bg="#F7F6ED")
root.geometry("1920x1080")

genders = ["Male", "Female"]
game_editions = get_active_game_editions()
edition_name_to_id = {name: id for name, id in game_editions.items()}

selected_name = tk.StringVar()
selected_gender = tk.StringVar(value="Male")
selected_race = tk.StringVar(value="Human")
selected_class = tk.StringVar(value="Fighter")
selected_background = tk.StringVar(value="Outlander")

dice_image = Image.open(get_resource_path(os.path.join("images", "dice.png")))
dice_image = dice_image.resize((40, 40), Image.Resampling.LANCZOS)
dice_icon = ImageTk.PhotoImage(dice_image)

# Initialize global variables
races = []
classes = []
backgrounds = []

def create_labeled_input(frame, label_text, options, selected_var, randomize_command):
    """Create a labeled input field with a dropdown and a randomize button."""
    tk.Label(frame, text=label_text, bg="#F7F6ED", fg="darkblue", font=("Arial", 20)).pack(side=tk.LEFT)
    create_dropdown(frame, options, selected_var)
    create_random_button(frame, randomize_command)

def create_dropdown(parent, options, selected_var):
    """Create a dropdown menu for selecting options."""
    dropdown = ttk.Combobox(parent, values=options, textvariable=selected_var, font=("Arial", 20))
    dropdown.pack(side=tk.LEFT, padx=5)
    dropdown.option_add('*TCombobox*Listbox.font', ("Arial", 20))
    dropdown.bind("<<ComboboxSelected>>", update_descriptions)
    return dropdown

def create_random_button(parent, command):
    """Create a button that triggers a randomization function."""
    tk.Button(parent, image=dice_icon, command=command, bg="#F7F6ED", bd=0).pack(side=tk.LEFT, padx=5)

def randomize_name():
    """Randomize the character name."""
    selected_name.set(get_random_name())

def randomize_gender():
    """Randomize the character gender."""
    selected_gender.set(random.choice(genders))

def randomize_race():
    """Randomize the character race."""
    if races:
        selected_race.set(random.choice(races))
    update_descriptions()

def randomize_class():
    """Randomize the character class."""
    if classes:
        selected_class.set(random.choice(classes))
    update_descriptions()

def randomize_background():
    """Randomize the character background."""
    selected_background.set(random.choice(backgrounds))
    update_descriptions()

def update_classes():
    """Update the class options based on selected game editions."""
    active_editions = [edition for edition, var in selected_editions.items() if var.get()]
    global classes
    classes = get_classes(active_editions)
    class_dropdown['values'] = classes
    selected_class.set(classes[0] if classes else "")
    update_descriptions()

def update_races():
    """Update the race options based on selected game editions."""
    active_editions = [edition_name_to_id[edition] for edition, var in selected_editions.items() if var.get()]
    global races
    races = get_races_for_editions(active_editions)
    race_dropdown['values'] = races
    selected_race.set(races[0] if races else "")
    update_descriptions()

def update_backgrounds():
    """Update the background options based on the selected game editions."""
    active_editions = [edition_name_to_id[edition] for edition, var in selected_editions.items() if var.get()]
    global backgrounds
    backgrounds = get_backgrounds(active_editions)
    background_dropdown['values'] = backgrounds
    selected_background.set(backgrounds[0] if backgrounds else "")
    update_descriptions()

def create_checkbox_command(option):
    """Create a unique command function for each checkbox."""
    def command():
        update_classes()
        update_races()
        update_backgrounds()
    return command

def create_checkbox_list(frame, label_text, options, selected_vars):
    """Create a list of checkboxes for selecting game editions."""
    tk.Label(frame, text=label_text, bg="#F7F6ED", fg="darkblue", font=("Arial", 20)).pack(anchor=tk.W)
    for option in options:
        var = tk.BooleanVar(value=(option == "Champion"))
        checkbox = tk.Checkbutton(frame, text=option, variable=var, bg="#F7F6ED", font=("Arial", 20),
                       command=create_checkbox_command(option))
        checkbox.pack(anchor=tk.W)
        checkbox.bind("<Enter>", lambda e, opt=option: show_edition_description(opt))
        checkbox.bind("<Leave>", lambda e: hide_edition_description())
        selected_vars[option] = var

def validate_inputs(data):
    """Validate inputs before inserting into the database."""
    if not data["name"]:
        return False, "Name is required."
    if data["gender"] not in genders:
        return False, "Invalid gender."
    if not data["game_editions"]:
        return False, "At least one game edition must be selected."
    if not data["race"]:
        return False, "Race is required."
    if not data["class"]:
        return False, "Class is required."
    if not data["background"]:
        return False, "Background is required."
    return True, ""

def create_temporary_character(character_data):
    """Create a temporary character in the database."""
    try:
        with closing(sqlite3.connect(DB_PATH)) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('''
                    INSERT INTO temporary_characters 
                    (name, gender, game_editions, race, class, background) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    character_data["name"],
                    character_data["gender"],
                    json.dumps(character_data["game_editions"]),
                    character_data["race"],
                    character_data["class"],
                    character_data["background"]
                ))
                temp_character_id = cursor.lastrowid
            conn.commit()
        return temp_character_id
    except sqlite3.Error as e:
        logger.error(f"Database error occurred: {e}")
        return None

def finalise_character():
    """Finalize character creation by saving to the database and running creator script."""
    character_data = {
        "name": selected_name.get() or get_random_name(),
        "gender": selected_gender.get(),
        "game_editions": [edition for edition, var in selected_editions.items() if var.get()],
        "race": selected_race.get(),
        "class": selected_class.get(),
        "background": selected_background.get()
    }
    
    # Print the values of the global variables
    print("Name:", character_data["name"])
    print("Gender:", character_data["gender"])
    print("Game Editions:", character_data["game_editions"])
    print("Race:", character_data["race"])
    print("Class:", character_data["class"])
    print("Background:", character_data["background"])
    
    temp_character_id = create_temporary_character(character_data)
    if temp_character_id:
        subprocess.run(['python', get_resource_path('creator.py'), str(temp_character_id)])
    else:
        logger.error("Failed to create temporary character")

def update_descriptions(event=None):
    """Update the descriptions based on the selected background, lineage, and class."""
    background = selected_background.get()
    race = selected_race.get()
    class_name = selected_class.get()

    with closing(sqlite3.connect(DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT desc_text FROM backgrounds WHERE name=?", (background,))
            background_desc = cursor.fetchone()
            cursor.execute("SELECT heritage_text FROM lineages WHERE name=?", (race,))
            lineage_desc = cursor.fetchone()
            cursor.execute("SELECT flavour_text FROM classes WHERE name=?", (class_name,))
            class_desc = cursor.fetchone()

    background_desc_label.config(text=background_desc[0] if background_desc else "")
    lineage_desc_label.config(text=lineage_desc[0] if lineage_desc else "")
    class_desc_label.config(text=class_desc[0] if class_desc else "")

def show_edition_description(edition):
    """Show the description of the game edition on mouse over."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT fluff_description FROM gameeditions WHERE name=?", (edition,))
            description = cursor.fetchone()
    edition_desc_label.config(text=description[0] if description else "")

def hide_edition_description():
    """Hide the game edition description when mouse leaves."""
    edition_desc_label.config(text="")

# Create the main layout
content_frame = tk.Frame(root, bg="#F7F6ED")
content_frame.place(relx=0.1, rely=0.1, relwidth=0.6, relheight=0.8)

frame = tk.Frame(content_frame, bg="#F7F6ED")
frame.pack(pady=10)
tk.Label(frame, text="Name:", bg="#F7F6ED", fg="darkblue", font=("Arial", 20)).pack(side=tk.LEFT)
tk.Entry(frame, textvariable=selected_name, font=("Arial", 20)).pack(side=tk.LEFT, padx=5)
create_random_button(frame, randomize_name)

frame1 = tk.Frame(content_frame, bg="#F7F6ED")
frame1.pack(pady=10)
create_labeled_input(frame1, "Gender:", genders, selected_gender, randomize_gender)

frame_bg = tk.Frame(content_frame, bg="#F7F6ED")
frame_bg.pack(pady=10, fill='x')
tk.Label(frame_bg, text="Background:", bg="#F7F6ED", fg="darkblue", font=("Arial", 20)).pack(side=tk.LEFT)
background_dropdown = create_dropdown(frame_bg, [], selected_background)
create_random_button(frame_bg, randomize_background)

frame2 = tk.Frame(content_frame, bg="#F7F6ED")
frame2.pack(pady=10)
tk.Label(frame2, text="Lineage:", bg="#F7F6ED", fg="darkblue", font=("Arial", 20)).pack(side=tk.LEFT)
race_dropdown = create_dropdown(frame2, [], selected_race)
create_random_button(frame2, randomize_race)

frame3 = tk.Frame(content_frame, bg="#F7F6ED")
frame3.pack(pady=10)
tk.Label(frame3, text="Class:", bg="#F7F6ED", fg="darkblue", font=("Arial", 20)).pack(side=tk.LEFT)
class_dropdown = create_dropdown(frame3, [], selected_class)
create_random_button(frame3, randomize_class)

# Descriptions area at the bottom left
description_frame = tk.Frame(root, bg="#F7F6ED")
description_frame.place(relx=0.1, rely=0.7, relwidth=0.6, relheight=0.2)

background_desc_label = tk.Label(description_frame, text="", bg="#F7F6ED", fg="black", font=("Arial", 14), wraplength=800, justify=tk.LEFT)
background_desc_label.pack(anchor='w', pady=5)

lineage_desc_label = tk.Label(description_frame, text="", bg="#F7F6ED", fg="black", font=("Arial", 14), wraplength=800, justify=tk.LEFT)
lineage_desc_label.pack(anchor='w', pady=5)

class_desc_label = tk.Label(description_frame, text="", bg="#F7F6ED", fg="black", font=("Arial", 14), wraplength=800, justify=tk.LEFT)
class_desc_label.pack(anchor='w', pady=5)

# Game Edition Selection and Finalize Button on the right
edition_frame = tk.Frame(root, bg="#F7F6ED")
edition_frame.place(relx=0.6, rely=0.1, relwidth=0.35, relheight=0.8)

selected_editions = {}
create_checkbox_list(edition_frame, "Game Edition:", game_editions.keys(), selected_editions)

edition_desc_label = tk.Label(edition_frame, text="", bg="#F7F6ED", fg="darkgray", font=("Arial", 12), wraplength=200, justify=tk.LEFT)
edition_desc_label.pack(anchor='w', padx=10)

finalise_button = tk.Button(edition_frame, text="Finalise", command=finalise_character, bg="#F7F6ED", fg="darkblue", font=("Arial", 20))
finalise_button.pack(pady=20)

update_backgrounds()
root.mainloop()
