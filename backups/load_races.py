import sqlite3
import json
import os

def load_races(json_file, db_connection):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    cursor = db_connection.cursor()
    
    for race in data['race']:
        name = race.get('name', '')
        source = race.get('source', '')
        page = race.get('page', 0)
        size = ','.join(race.get('size', []))
        darkvision = race.get('darkvision', 0)
        creature_types = ','.join(race.get('creatureTypes', []))
        creature_type_tags = ','.join(race.get('creatureTypeTags', []))
        age = json.dumps(race.get('age', {}))
        lineage = race.get('lineage', '')

        # Insert into races table
        cursor.execute('''
        INSERT INTO races (name, source, page, size, darkvision, creature_types, creature_type_tags, age, lineage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, source, page, size, darkvision, creature_types, creature_type_tags, age, lineage))
        race_id = cursor.lastrowid
        
        # Insert into abilities table
        for ability in race.get('ability', []):
            for ability_type, value in ability.items():
                if isinstance(value, dict):
                    value = json.dumps(value)  # Convert dict to JSON string
                cursor.execute('''
                INSERT INTO abilities (race_id, ability_type, value)
                VALUES (?, ?, ?)
                ''', (race_id, ability_type, value))
        
        # Handle speed field, which can be either a dictionary or an integer
        speed = race.get('speed', {})
        if isinstance(speed, dict):
            walk_speed = speed.get('walk', 0)
            fly_speed = speed.get('fly', 0)
            swim_speed = speed.get('swim', 0)
        else:
            walk_speed = speed
            fly_speed = 0
            swim_speed = 0

        # Insert into speed table
        cursor.execute('''
        INSERT INTO speed (race_id, walk, fly, swim)
        VALUES (?, ?, ?, ?)
        ''', (race_id, walk_speed, fly_speed, swim_speed))
        
        # Insert into language_proficiencies table
        for language in race.get('languageProficiencies', []):
            lang = language.get('language', '')
            proficiency = language.get('proficiency', '')
            cursor.execute('''
            INSERT INTO language_proficiencies (race_id, language, proficiency_level)
            VALUES (?, ?, ?)
            ''', (race_id, lang, proficiency))
        
        # Insert into entries table
        for entry in race.get('entries', []):
            if isinstance(entry, str):
                entry_name = ''
                entry_type = ''
                content = entry
            else:
                entry_name = entry.get('name', '')
                entry_type = entry.get('type', '')
                content = json.dumps(entry.get('entries', entry.get('items', [])))
            cursor.execute('''
            INSERT INTO entries (race_id, name, type, content)
            VALUES (?, ?, ?, ?)
            ''', (race_id, entry_name, entry_type, content))
    
    db_connection.commit()

def main():
    script_dir = os.path.dirname(__file__)
    json_path = os.path.join(script_dir, 'races.json')
    
    conn = sqlite3.connect('game_database.db')
    load_races(json_path, conn)
    conn.close()

if __name__ == "__main__":
    main()
