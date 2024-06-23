import sqlite3

def setup_database():
    conn = sqlite3.connect('game_database.db')
    cursor = conn.cursor()

    # Drop the existing characters table if it exists
    cursor.execute("DROP TABLE IF EXISTS characters")

    # Create the new characters table
    cursor.execute('''
        CREATE TABLE characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gender TEXT,
            class TEXT,
            race TEXT,
            background TEXT,
            strength INTEGER,
            intelligence INTEGER,
            wisdom INTEGER,
            dexterity INTEGER,
            constitution INTEGER,
            charisma INTEGER,
            level INTEGER,
            experience_points INTEGER,
            proficiency_bonus INTEGER,
            hit_points INTEGER,
            armor_class INTEGER,
            skillProficiencies TEXT,
            languageProficiencies TEXT,
            startingEquipment TEXT,
            entries TEXT
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()
