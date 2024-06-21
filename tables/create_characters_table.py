import sqlite3

def create_characters_table():
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

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_characters_table()
