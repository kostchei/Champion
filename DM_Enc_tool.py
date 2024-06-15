# DM_Enc_tool.py
import tkinter as tk
from tkinter import ttk
import os
import subprocess
import sys

# Create the main application window
root = tk.Tk()
root.title("Encounter Generator")
root.geometry("800x600")
root.configure(bg="#F7F6ED")  # Buff color

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
    
# Create and place widgets
tk.Label(root, text="Number of Characters:", bg="#F7F6ED", fg="darkblue", font=("Arial", 24)).pack(pady=10)
num_char_dropdown = ttk.Combobox(root, values=num_characters, textvariable=selected_characters, font=("Arial", 24))
num_char_dropdown.pack()

tk.Label(root, text="Level of Characters:", bg="#F7F6ED", fg="darkblue", font=("Arial", 24)).pack(pady=10)
level_dropdown = ttk.Combobox(root, values=character_levels, textvariable=selected_level, font=("Arial", 24))
level_dropdown.pack()

tk.Label(root, text="Difficulty Level:", bg="#F7F6ED", fg="darkblue", font=("Arial", 24)).pack(pady=10)
difficulty_dropdown = ttk.Combobox(root, values=difficulty_levels, textvariable=selected_difficulty, font=("Arial", 24))
difficulty_dropdown.pack()

tk.Label(root, text="Terrain Type:", bg="#F7F6ED", fg="darkblue", font=("Arial", 24)).pack(pady=10)
terrain_dropdown = ttk.Combobox(root, values=terrain_types, textvariable=selected_terrain, font=("Arial", 24))
terrain_dropdown.pack()

tk.Label(root, text="Realm:", bg="#F7F6ED", fg="darkblue", font=("Arial", 24)).pack(pady=10)
realm_dropdown = ttk.Combobox(root, values=realm_files, textvariable=selected_realm, font=("Arial", 24))
realm_dropdown.pack()

generate_button = tk.Button(root, text="Generate", command=run_encounter_generation, bg="#F7F6ED", fg="darkblue", font=("Arial", 24))
generate_button.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()
