import json
import os
import numpy as np
import hexy as hx
import random
from datetime import datetime

HEX_RADIUS = 30
script_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(script_dir, "images")

terrain_types = {
    "forest": "forest.png",
    "open": "open.png",
    "hill": "hill.png",
    "water": "water.png",
    "settlement": "settlement.png"
}

# Ensure the images directory exists and contains the necessary files
for terrain, filename in terrain_types.items():
    image_path = os.path.join(images_dir, filename)
    if not os.path.isfile(image_path):
        print(f"Error: Image file for terrain '{terrain}' not found at '{image_path}'")
        exit(1)

terrain_probabilities = {
    "forest": 0.75,
    "hill": 0.10,
    "open": 0.10,
    "water": 0.03,
    "settlement": 0.02
}

class ExampleHex:
    def __init__(self, cube_coordinates, terrain):
        self.cube_coordinates = cube_coordinates
        self.terrain = terrain

class ExampleHexMap:
    def __init__(self, max_coord=15):
        self.hex_map = {}
        self.max_coord = max_coord

        all_coordinates = hx.get_disk(np.array((0, 0, 0)), self.max_coord)
        terrain_choices = list(terrain_probabilities.keys())
        terrain_weights = list(terrain_probabilities.values())

        for cube in all_coordinates:
            terrain = random.choices(terrain_choices, weights=terrain_weights, k=1)[0]
            self.hex_map[tuple(cube)] = ExampleHex(cube.tolist(), terrain)

    def save_to_json(self, filename):
        hex_map_data = {json.dumps(key): {"cube": hex.cube_coordinates, "terrain": hex.terrain} for key, hex in self.hex_map.items()}
        with open(filename, 'w') as file:
            json.dump(hex_map_data, file)

try:
    hex_map = ExampleHexMap()

    # Generate a dynamic filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hex_map_{timestamp}.json"

    hex_map.save_to_json(os.path.join(script_dir, filename))
    print(f"Map saved as {filename}")
except Exception as e:
    print(f"An error occurred: {e}")
