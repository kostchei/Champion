import sqlite3

def create_backgrounds_table():
    conn = sqlite3.connect('game_database.db')
    cursor = conn.cursor()

    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS backgrounds')
    cursor.execute('DROP TABLE IF EXISTS proficiencies')
    cursor.execute('DROP TABLE IF EXISTS equipment')
    cursor.execute('DROP TABLE IF EXISTS entries')

    # Create new tables with the correct schema
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS backgrounds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        skillProficiencies TEXT,
        languageProficiencies TEXT,
        startingEquipment TEXT,
        entries TEXT,
        features TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS proficiencies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        background_id INTEGER,
        type TEXT,
        name TEXT,
        count INTEGER,
        FOREIGN KEY(background_id) REFERENCES backgrounds(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        background_id INTEGER,
        character_id INTEGER,
        name TEXT,
        description TEXT,
        attribute_bonus TEXT,
        image_path TEXT,
        FOREIGN KEY(background_id) REFERENCES backgrounds(id),
        FOREIGN KEY(character_id) REFERENCES characters(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        background_id INTEGER,
        type TEXT,
        name TEXT,
        entry TEXT,
        FOREIGN KEY(background_id) REFERENCES backgrounds(id)
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_backgrounds_table()
