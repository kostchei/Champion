import sqlite3

def create_classes_table():
    conn = sqlite3.connect('game_database.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        hit_die TEXT,
        primary_ability TEXT,
        saves TEXT,
        source TEXT,
        page INTEGER
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_classes_table()
