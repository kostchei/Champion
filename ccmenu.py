import tkinter as tk
from tkinter import ttk
import json
import os
import subprocess
import random
from PIL import Image, ImageTk

# Adjust these imports to match your file structure
from utils.names import get_random_name
from utils.game_editions import get_active_game_editions
from utils.races import get_races, get_race_details
from utils.classes import get_classes, get_class_details
from utils.backgrounds import get_backgrounds, get_background_details

# Create the main application window first
root = tk.Tk()
root.title("Character Generator")
root.configure(bg="#F7F6ED")

# Set default window size
root.geometry("1920x1080")

# Lists of options
genders = ["Male", "Female"]
game_editions = get_active_game_editions()
races = get_races()
backgrounds = get_backgrounds()

# Global variables for selected values with default selections
selected_name = tk.StringVar()
selected_gender = tk.StringVar(value="Male")
selected_race = tk.StringVar(value="Human")
selected_class = tk.StringVar(value="Fighter")
selected_background = tk.StringVar(value="Outlander")

# Load dice icon
dice_image = Image.open("./images/dice.png")
dice_image = dice_image.resize((40, 40), Image.Resampling.LANCZOS)
dice_icon = ImageTk.PhotoImage(dice_image)

# Function to create labeled input with randomize button
def create_labeled_input(frame, label_text, options, selected_var, randomize_command):
    tk.Label(frame, text=label_text, bg="#F7F6ED", fg="darkblue", font=("Arial", 20)).pack(side=tk.LEFT)
    create_dropdown(frame, options, selected_var)
    create_random_button(frame, randomize_command)

# Function to create dropdown menus
def create_dropdown(parent, options, selected_var):
    dropdown = ttk.Combobox(parent, values=options, textvariable=selected_var, font=("Arial", 20))
    dropdown.pack(side=tk.LEFT, padx=5)
    dropdown.option_add('*TCombobox*Listbox.font', ("Arial", 20))
    return dropdown

# Function to create randomize buttons with dice icon
def create_random_button(parent, command):
    button = tk.Button(parent, image=dice_icon, command=command, bg="#F7F6ED", bd=0)
    button.pack(side=tk.LEFT, padx=5)

# Create functions for randomization
def randomize_name():
    selected_name.set(get_random_name())

def randomize_gender():
    selected_gender.set(random.choice(genders))

def randomize_race():
    selected_race.set(random.choice(races))

def randomize_class():
    if classes:
        selected_class.set(random.choice(classes))

def randomize_background():
    selected_background.set(random.choice(backgrounds))

# Function to update class options based on selected game editions
def update_classes():
    active_editions = [edition for edition, var in selected_editions.items() if var.get()]
    print(f"Active Editions: {active_editions}")  # Debug print
    global classes
    classes = get_classes(active_editions)
    print(f"Classes fetched: {classes}")  # Debug print
    class_dropdown['values'] = classes
    selected_class.set(classes[0] if classes else "")

# Function to create checkboxes for game editions
def create_checkbox_list(frame, label_text, options, selected_vars):
    tk.Label(frame, text=label_text, bg="#F7F6ED", fg="darkblue", font=("Arial", 20)).pack(anchor=tk.W)
    for option in options:
        var = tk.BooleanVar(value=(option == "Champion"))  # Select Champion by default
        checkbox = tk.Checkbutton(frame, text=option, variable=var, bg="#F7F6ED", font=("Arial", 20),
                                  command=update_classes)  # Update classes when checkbox is toggled
        checkbox.pack(anchor=tk.W)
        selected_vars[option] = var

# Centralize content using place
content_frame = tk.Frame(root, bg="#F7F6ED")
content_frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

# Create the GUI layout
frame = tk.Frame(content_frame, bg="#F7F6ED")
frame.pack(pady=20)

tk.Label(frame, text="Name:", bg="#F7F6ED", fg="darkblue", font=("Arial", 20)).pack(side=tk.LEFT)
name_entry = tk.Entry(frame, textvariable=selected_name, font=("Arial", 20))
name_entry.pack(side=tk.LEFT, padx=5)
create_random_button(frame, randomize_name)

# First row frame
frame1 = tk.Frame(content_frame, bg="#F7F6ED")
frame1.pack(pady=20)

create_labeled_input(frame1, "Gender:", genders, selected_gender, randomize_gender)
create_labeled_input(frame1, "Background:", backgrounds, selected_background, randomize_background)

# Second row frame
frame2 = tk.Frame(content_frame, bg="#F7F6ED")
frame2.pack(pady=20)

create_labeled_input(frame2, "Race:", races, selected_race, randomize_race)
class_dropdown = create_dropdown(frame2, [], selected_class)
create_random_button(frame2, randomize_class)

# Third row frame for Game Edition
frame3 = tk.Frame(content_frame, bg="#F7F6ED")
frame3.pack(pady=20)

selected_editions = {}
create_checkbox_list(frame3, "Game Edition:", game_editions, selected_editions)

# Function to finalise character and save data
def finalise_character():
    character_data = {
        "name": selected_name.get() or get_random_name(),
        "gender": selected_gender.get(),
        "game_editions": [edition for edition, var in selected_editions.items() if var.get()],
        "race": selected_race.get(),
        "class": selected_class.get(),
        "background": selected_background.get()
    }
    
    # Get detailed class information
    class_details = get_class_details(character_data["class"])
    character_data.update(class_details)
    
    # Get detailed race information
    race_details = get_race_details(character_data["race"])
    character_data.update(race_details)

    # Get detailed background information
    background_details = get_background_details(character_data["background"])
    character_data.update(background_details)

    if not os.path.exists('./saves'):
        os.makedirs('./saves')
    with open('./saves/character.json', 'w') as f:
        json.dump(character_data, f)

    subprocess.run(['python', 'creator.py', './saves/character.json'])

# Add finalise button
finalise_button = tk.Button(content_frame, text="Finalise", command=finalise_character, bg="#F7F6ED", fg="darkblue", font=("Arial", 20))
finalise_button.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()
