import sqlite3

def create_races_table():
    conn = sqlite3.connect('game_database.db')
    cursor = conn.cursor()

    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS races')
    cursor.execute('DROP TABLE IF EXISTS abilities')
    cursor.execute('DROP TABLE IF EXISTS speed')
    cursor.execute('DROP TABLE IF EXISTS language_proficiencies')
    cursor.execute('DROP TABLE IF EXISTS entries')

    # Create new tables with the correct schema
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS races (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        source TEXT,
        page INTEGER,
        size TEXT,
        darkvision INTEGER,
        creature_types TEXT,
        creature_type_tags TEXT,
        age TEXT,
        lineage TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS abilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        race_id INTEGER,
        ability_type TEXT,
        value INTEGER,
        FOREIGN KEY(race_id) REFERENCES races(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS speed (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        race_id INTEGER,
        walk INTEGER,
        fly INTEGER,
        swim INTEGER,
        FOREIGN KEY(race_id) REFERENCES races(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS language_proficiencies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        race_id INTEGER,
        language TEXT,
        proficiency_level TEXT,
        FOREIGN KEY(race_id) REFERENCES races(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        race_id INTEGER,
        name TEXT,
        type TEXT,
        content TEXT,
        FOREIGN KEY(race_id) REFERENCES races(id)
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_races_table()
