import sqlite3
import json
import os

def create_tables(db_connection):
    cursor = db_connection.cursor()

    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS lineages')
    cursor.execute('DROP TABLE IF EXISTS abilities')
    cursor.execute('DROP TABLE IF EXISTS speed')
    cursor.execute('DROP TABLE IF EXISTS language_proficiencies')
    cursor.execute('DROP TABLE IF EXISTS entries')
    cursor.execute('DROP TABLE IF EXISTS subraces')

    # Create new tables with the correct schema
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lineages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        size TEXT,
        darkvision INTEGER,
        creature_types TEXT,
        creature_type_tags TEXT,
        lineage TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS abilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        race_id INTEGER,
        ability_type TEXT,
        value INTEGER,
        FOREIGN KEY(race_id) REFERENCES lineages(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS speed (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        race_id INTEGER,
        walk INTEGER,
        fly INTEGER,
        swim INTEGER,
        FOREIGN KEY(race_id) REFERENCES lineages(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS language_proficiencies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        race_id INTEGER,
        language TEXT,
        proficiency_level TEXT,
        FOREIGN KEY(race_id) REFERENCES lineages(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        race_id INTEGER,
        name TEXT,
        type TEXT,
        content TEXT,
        FOREIGN KEY(race_id) REFERENCES lineages(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subraces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        race_id INTEGER,
        name TEXT,
        FOREIGN KEY(race_id) REFERENCES lineages(id)
    )
    ''')

    db_connection.commit()

def load_lineages(json_file, db_connection):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    cursor = db_connection.cursor()
    
    # Set to track unique lineage names
    lineage_names = set()

    for race in data['race']:
        name = race.get('name', '')
        
        if name in lineage_names:
            continue  # Skip duplicate lineage names
        lineage_names.add(name)

        # Check if lineage already exists
        cursor.execute('SELECT id FROM lineages WHERE name = ?', (name,))
        if cursor.fetchone():
            continue  # Skip if lineage already exists

        size = ','.join(race.get('size', []))
        darkvision = race.get('darkvision', 0)
        creature_types = ','.join(race.get('creatureTypes', []))
        creature_type_tags = ','.join(race.get('creatureTypeTags', []))
        lineage = race.get('lineage', '')

        # Insert into lineages table
        cursor.execute('''
        INSERT INTO lineages (name, size, darkvision, creature_types, creature_type_tags, lineage)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, size, darkvision, creature_types, creature_type_tags, lineage))
        lineage_id = cursor.lastrowid
        
        # Insert into abilities table
        for ability in race.get('ability', []):
            for ability_type, value in ability.items():
                if isinstance(value, dict):
                    value = json.dumps(value)  # Convert dict to JSON string
                cursor.execute('''
                INSERT INTO abilities (race_id, ability_type, value)
                VALUES (?, ?, ?)
                ''', (lineage_id, ability_type, value))
        
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
        ''', (lineage_id, walk_speed, fly_speed, swim_speed))
        
        # Insert into language_proficiencies table
        for language in race.get('languageProficiencies', []):
            lang = language.get('language', '')
            proficiency = language.get('proficiency', '')
            cursor.execute('''
            INSERT INTO language_proficiencies (race_id, language, proficiency_level)
            VALUES (?, ?, ?)
            ''', (lineage_id, lang, proficiency))
        
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
            ''', (lineage_id, entry_name, entry_type, content))
    
    db_connection.commit()

def load_subraces(json_file, db_connection):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    cursor = db_connection.cursor()

    for subrace in data['subrace']:
        name = subrace.get('name', '')
        race_name = subrace.get('raceName', '')

        # Find the lineage_id from the lineages table
        cursor.execute('SELECT id FROM lineages WHERE name = ?', (race_name,))
        lineage_id = cursor.fetchone()
        if lineage_id:
            lineage_id = lineage_id[0]
        else:
            continue  # Skip if the parent lineage is not found

        # Insert into subraces table
        cursor.execute('''
        INSERT INTO subraces (race_id, name)
        VALUES (?, ?)
        ''', (lineage_id, name))
        subrace_id = cursor.lastrowid

        # Insert into abilities table
        for ability in subrace.get('ability', []):
            for ability_type, value in ability.items():
                if isinstance(value, dict):
                    value = json.dumps(value)  # Convert dict to JSON string
                cursor.execute('''
                INSERT INTO abilities (race_id, ability_type, value)
                VALUES (?, ?, ?)
                ''', (subrace_id, ability_type, value))
        
        # Insert into entries table
        for entry in subrace.get('entries', []):
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
            ''', (subrace_id, entry_name, entry_type, content))

    db_connection.commit()

def main():
    script_dir = os.path.dirname(__file__)
    json_path = os.path.join(script_dir, 'races.json')
    
    conn = sqlite3.connect('game_database.db')
    create_tables(conn)
    load_lineages(json_path, conn)
    load_subraces(json_path, conn)
    conn.close()

if __name__ == "__main__":
    main()
