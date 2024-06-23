#/tables/create_lineage_table.py
import sqlite3

def create_lineages_table():
    conn = sqlite3.connect('game_database.db')
    cursor = conn.cursor()

    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS lineages')
    cursor.execute('DROP TABLE IF EXISTS abilities')
    cursor.execute('DROP TABLE IF EXISTS speed')
    cursor.execute('DROP TABLE IF EXISTS language_proficiencies')
    cursor.execute('DROP TABLE IF EXISTS entries')

    # Create new tables with the correct schema
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lineages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
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
        lineage_id INTEGER,
        ability_type TEXT,
        value INTEGER,
        FOREIGN KEY(lineage_id) REFERENCES lineages(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS speed (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lineage_id INTEGER,
        walk INTEGER,
        fly INTEGER,
        swim INTEGER,
        FOREIGN KEY(lineage_id) REFERENCES lineages(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS language_proficiencies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lineage_id INTEGER,
        language TEXT,
        proficiency_level TEXT,
        FOREIGN KEY(lineage_id) REFERENCES lineages(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lineage_id INTEGER,
        name TEXT,
        type TEXT,
        content TEXT,
        FOREIGN KEY(lineage_id) REFERENCES lineages(id)
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_lineages_table()
