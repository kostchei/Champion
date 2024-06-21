import sqlite3
import json
import os

def load_backgrounds(json_file, db_connection):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    cursor = db_connection.cursor()

    for background in data['background']:
        name = background['name']
        skillProficiencies = json.dumps(background.get('skillProficiencies', []))
        languageProficiencies = json.dumps(background.get('languageProficiencies', []))
        startingEquipment = json.dumps(background.get('startingEquipment', []))
        entries = json.dumps(background.get('entries', []))
        features = json.dumps(background.get('features', []))

        cursor.execute('''
            INSERT INTO backgrounds (
                name, skillProficiencies, languageProficiencies,
                startingEquipment, entries, features
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            name, skillProficiencies, languageProficiencies,
            startingEquipment, entries, features
        ))

    db_connection.commit()

def main():
    # Use relative path
    script_dir = os.path.dirname(__file__)
    json_path = os.path.join(script_dir, 'backgrounds.json')
    
    conn = sqlite3.connect('game_database.db')
    load_backgrounds(json_path, conn)
    conn.close()

if __name__ == "__main__":
    main()
