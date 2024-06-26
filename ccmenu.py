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
backgrounds = get_backgrounds()
edition_name_to_id = {name: id for name, id in game_editions.items()}

selected_name = tk.StringVar()
selected_gender = tk.StringVar(value="Male")
selected_race = tk.StringVar(value="Human")
selected_class = tk.StringVar(value="Fighter")
selected_background = tk.StringVar(value="Outlander")
show_campaign_specific = tk.BooleanVar(value=False)

dice_image = Image.open(get_resource_path(os.path.join("images", "dice.png")))
dice_image = dice_image.resize((40, 40), Image.Resampling.LANCZOS)
dice_icon = ImageTk.PhotoImage(dice_image)

# Initialize global variables
races = []
classes = []

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

def randomize_class():
    """Randomize the character class."""
    if classes:
        selected_class.set(random.choice(classes))

def randomize_background():
    """Randomize the character background."""
    selected_background.set(random.choice(backgrounds))

def update_classes():
    """Update the class options based on selected game editions."""
    active_editions = [edition for edition, var in selected_editions.items() if var.get()]
    global classes
    classes = get_classes(active_editions)
    class_dropdown['values'] = classes
    selected_class.set(classes[0] if classes else "")

def update_races():
    """Update the race options based on selected game editions."""
    active_editions = [edition_name_to_id[edition] for edition, var in selected_editions.items() if var.get()]
    global races
    races = get_races_for_editions(active_editions)
    race_dropdown['values'] = races
    selected_race.set(races[0] if races else "")

def update_backgrounds():
    """Update the background options based on the campaign-specific filter."""
    global backgrounds
    backgrounds = get_backgrounds()
    if not show_campaign_specific.get():
        backgrounds = [bg for bg in backgrounds if not get_background_details(bg).get('campaign_specific', 0)]
    background_dropdown['values'] = backgrounds
    selected_background.set(backgrounds[0] if backgrounds else "")

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
        tk.Checkbutton(frame, text=option, variable=var, bg="#F7F6ED", font=("Arial", 20),
                       command=create_checkbox_command(option)).pack(anchor=tk.W)
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
background_dropdown = create_dropdown(frame_bg, backgrounds, selected_background)
create_random_button(frame_bg, randomize_background)
tk.Checkbutton(frame_bg, text="Show Campaign Specific", variable=show_campaign_specific, bg="#F7F6ED", font=("Arial", 20),
               command=update_backgrounds).pack(side=tk.LEFT, padx=5)

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

# Game Edition Selection and Finalize Button on the right
edition_frame = tk.Frame(root, bg="#F7F6ED")
edition_frame.place(relx=0.75, rely=0.1, relwidth=0.2, relheight=0.8)

selected_editions = {}
create_checkbox_list(edition_frame, "Game Edition:", game_editions.keys(), selected_editions)

finalise_button = tk.Button(edition_frame, text="Finalise", command=finalise_character, bg="#F7F6ED", fg="darkblue", font=("Arial", 20))
finalise_button.pack(pady=20)

update_backgrounds()
root.mainloop()
