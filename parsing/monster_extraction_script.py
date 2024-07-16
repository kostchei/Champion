#monster extraction script yo
import json
import os

def load_txt(txt_path):
    """Load the TXT file into a list of monster names."""
    with open(txt_path, 'r', encoding='utf-8') as file:
        content = file.read()
    monster_names = [name.strip() for name in content.split(',')]
    return monster_names

def extract_monsters(data):
    """Extract monsters from the JSON data, handling different structures."""
    if 'monster' in data:
        return data['monster']
    for key in data:
        if isinstance(data[key], dict) and 'monster' in data[key]:
            return data[key]['monster']
    return []

def load_json_files(folder_path):
    """Load all JSON files from the specified folder."""
    json_data = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                monsters = extract_monsters(data)
                if monsters:  # Skip files without any monsters
                    json_data.extend(monsters)
    return json_data

def filter_monsters(json_data, monster_names):
    """Filter the monsters based on the list of monster names."""
    return [monster for monster in json_data if monster['name'] in monster_names]

def save_filtered_data(filtered_data, output_path):
    """Save the filtered monster data to a new JSON file."""
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump({'monster': filtered_data}, file, indent=4)

def main(txt_path, folder_path, output_path):
    monster_names = load_txt(txt_path)
    json_data = load_json_files(folder_path)
    filtered_monsters = filter_monsters(json_data, monster_names)
    save_filtered_data(filtered_monsters, output_path)
    print(f"Filtered data saved to {output_path}")

# Example usage
txt_path = 'monsters.txt'
folder_path = r'D:\Code\5etools\data\bestiary'
output_path = 'completed_new.json'

main(txt_path, folder_path, output_path)
