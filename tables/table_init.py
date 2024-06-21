# ../tables/table_init.py

import sqlite3

def create_database():
    conn = sqlite3.connect('game_database.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        strength INTEGER,
        armour_class INTEGER,
        hit_points INTEGER,
        description TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS derived_values (
        id INTEGER PRIMARY KEY,
        character_id INTEGER,
        attribute_type TEXT,
        attribute TEXT,
        value TEXT,
        skill_proficiencies TEXT,
        feature TEXT,
        equipment TEXT,
        languages TEXT,
        tool_proficiencies TEXT,
        feats TEXT,
        spells TEXT,
        FOREIGN KEY(character_id) REFERENCES characters(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY,
        character_id INTEGER,
        property_type TEXT,
        property_description TEXT,
        FOREIGN KEY(character_id) REFERENCES characters(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        attribute_bonus TEXT,
        image_path TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS character_equipment (
        character_id INTEGER,
        equipment_id INTEGER,
        PRIMARY KEY(character_id, equipment_id),
        FOREIGN KEY(character_id) REFERENCES characters(id),
        FOREIGN KEY(equipment_id) REFERENCES equipment(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS realms (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        style TEXT,
        level_range TEXT,
        environment_type TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS realm_characters (
        realm_id INTEGER,
        character_id INTEGER,
        PRIMARY KEY(realm_id, character_id),
        FOREIGN KEY(realm_id) REFERENCES realms(id),
        FOREIGN KEY(character_id) REFERENCES characters(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS realm_equipment (
        realm_id INTEGER,
        equipment_id INTEGER,
        PRIMARY KEY(realm_id, equipment_id),
        FOREIGN KEY(realm_id) REFERENCES realms(id),
        FOREIGN KEY(equipment_id) REFERENCES equipment(id)
    )
    ''')

    conn.commit()
    conn.close()

# Run the create_database function to set up the database
if __name__ == "__main__":
    create_database()
