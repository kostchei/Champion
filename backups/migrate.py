import sqlite3
import os
from contextlib import closing

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Set the correct path for the database
DB_PATH = os.path.join(current_dir, 'game_database.db')

def migrate():
    """ Migrate the database schema to remove 'entries' column and add 'saves' column to the characters table. """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            # Drop the new table if it already exists
            cursor.execute('DROP TABLE IF EXISTS characters_new')
            
            # Create a temporary table with the new schema
            cursor.execute('''
                CREATE TABLE characters_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    gender TEXT,
                    game_editions TEXT,
                    race TEXT,
                    class TEXT,
                    background TEXT,
                    strength INTEGER,
                    intelligence INTEGER,
                    wisdom INTEGER,
                    dexterity INTEGER,
                    constitution INTEGER,
                    charisma INTEGER,
                    experience_points INTEGER,
                    skillProficiencies TEXT DEFAULT '[]',
                    languageProficiencies TEXT DEFAULT '[]',
                    expertise TEXT DEFAULT '[]',
                    craftingTools TEXT DEFAULT '[]',
                    vehicles TEXT DEFAULT '[]',
                    saves TEXT DEFAULT '[]'
                )
            ''')
            # Copy data from the old table to the new table, excluding the 'entries' column
            cursor.execute('''
                INSERT INTO characters_new (
                    id, name, gender, game_editions, race, class, background, 
                    strength, intelligence, wisdom, dexterity, constitution, charisma, 
                    experience_points, skillProficiencies, languageProficiencies
                )
                SELECT 
                    id, name, gender, game_editions, race, class, background, 
                    strength, intelligence, wisdom, dexterity, constitution, charisma, 
                    experience_points, skillProficiencies, languageProficiencies
                FROM characters
            ''')
            # Drop the old table and rename the new table to the old table's name
            cursor.execute('DROP TABLE characters')
            cursor.execute('ALTER TABLE characters_new RENAME TO characters')
            conn.commit()

if __name__ == "__main__":
    migrate()
    print("Migration completed successfully.")
