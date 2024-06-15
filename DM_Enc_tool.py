import tkinter as tk
from tkinter import ttk
import os
import subprocess
import sys

# Colors and fonts consistent with main.py
BG_COLOR = "#F7F6ED"  # Buff color
TEXT_COLOR = "#1E2832"  # Dark blue
BUTTON_BG_COLOR = "#F0F0E6"  # Grey (light background for buttons)
BUTTON_FG_COLOR = "#1E2832"  # Dark blue (text on buttons)
FONT = ("Arial", 18)  # Smaller font

# Create the main application window
root = tk.Tk()
root.title("Encounter Generator")
root.geometry("1920x1080")
root.configure(bg=BG_COLOR)

# Options for dropdowns
num_characters = [str(i) for i in range(1, 7)]
character_levels = [str(i) for i in range(1, 22)]
difficulty_levels = ["random", "easy", "medium", "hard", "deadly"]
terrain_types = ["open", "forest", "hills", "mountains", "dense"]
realm_files = [f.split('.')[0] for f in os.listdir("realms") if f.endswith(".json")]

# Global variables for selected values with default selections
selected_characters = tk.StringVar(value=num_characters[0])
selected_level = tk.StringVar(value=character_levels[0])
selected_difficulty = tk.StringVar(value=difficulty_levels[0])
selected_terrain = tk.StringVar(value=terrain_types[0])
selected_realm = tk.StringVar(value=realm_files[0])

# Function to run the encounter generation script
def run_encounter_generation():
    party_size = selected_characters.get()
    party_level = selected_level.get()
    difficulty = selected_difficulty.get()
    terrain = selected_terrain.get()
    realm = selected_realm.get()

    script_path = os.path.join("utils", "encounter_generation.py")
    
    # Run the encounter generation script
    subprocess.run([sys.executable, script_path, party_size, party_level, difficulty, terrain, realm])
    
# Create and place widgets with consistent styling
def create_label(text):
    return tk.Label(root, text=text, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT)

def create_dropdown(values, variable):
    dropdown = ttk.Combobox(root, values=values, textvariable=variable, font=FONT)
    dropdown.pack(pady=10)
    return dropdown

def create_button(text, command):
    button = tk.Button(root, text=text, command=command, bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, font=FONT)
    button.pack(pady=20)
    return button

create_label("Number of Characters:").pack(pady=10)
create_dropdown(num_characters, selected_characters)

create_label("Level of Characters:").pack(pady=10)
create_dropdown(character_levels, selected_level)

create_label("Difficulty Level:").pack(pady=10)
create_dropdown(difficulty_levels, selected_difficulty)

create_label("Terrain Type:").pack(pady=10)
create_dropdown(terrain_types, selected_terrain)

create_label("Realm:").pack(pady=10)
create_dropdown(realm_files, selected_realm)

create_button("Generate", run_encounter_generation)

# Run the Tkinter event loop
root.mainloop()
