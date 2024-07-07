# create_tables.py

import sqlite3

def get_db_connection():
    """ Get a database connection. """
    db_path = './tables/game_database.db'
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def create_tables():
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()

    # Create character_skills table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS character_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            skill TEXT NOT NULL,
            value INTEGER NOT NULL,
            FOREIGN KEY (character_id) REFERENCES characters(id)
        )
    ''')

    # Create character_saves table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS character_saves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            save TEXT NOT NULL,
            value INTEGER NOT NULL,
            FOREIGN KEY (character_id) REFERENCES characters(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
