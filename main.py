import os
import subprocess
import sys
import json
import pygame as pg
import hexy as hx
import numpy as np
from datetime import datetime

# Ensure hexmap.py and explorer.py are in the same directory
script_dir = os.path.dirname(os.path.abspath(__file__))
hexmap_file = os.path.join(script_dir, "hexmap.py")
explorer_file = os.path.join(script_dir, "explorer.py")

def load_hex_map(filename):
    with open(filename, 'r') as file:
        hex_map_data = json.load(file)
    return hex_map_data

def main():
    print("1. Generate new map")
    print("2. Load existing map")
    choice = input("Enter your choice: ")

    if choice == '1':
        # Run overland.py to generate a new map
        subprocess.run([sys.executable, os.path.join(script_dir, "overland.py")])
        
        # Find the latest generated map
        generated_files = [f for f in os.listdir(script_dir) if f.startswith("hex_map_") and f.endswith(".json")]
        if not generated_files:
            print("No maps generated. Exiting.")
            return
        
        latest_map = max(generated_files, key=lambda f: os.path.getctime(os.path.join(script_dir, f)))
        filename = os.path.join(script_dir, latest_map)
        print(f"Loading the latest generated map: {filename}")
    elif choice == '2':
        filename = input("Enter the filename of the map to load: ")
        filename = os.path.join(script_dir, filename)
        if not os.path.exists(filename):
            print("File does not exist. Exiting.")
            return
    else:
        print("Invalid choice. Exiting.")
        return
    
    # Load and display the map using explorer.py
    subprocess.run([sys.executable, explorer_file, filename])

if __name__ == '__main__':
    main()
