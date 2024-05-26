import os
import json
from datetime import datetime

def load_most_recent_character():
    saves_dir = "./saves"
    if not os.path.exists(saves_dir):
        return None
    
    character_files = [os.path.join(saves_dir, f) for f in os.listdir(saves_dir) if f.endswith('.json')]
    characters = []

    for file in character_files:
        with open(file, 'r') as f:
            data = json.load(f)
            if data.get('dead', False) == False:
                characters.append((file, data))

    if not characters:
        return None

    characters.sort(key=lambda x: os.path.getmtime(x[0]), reverse=True)
    return characters[0][1]
