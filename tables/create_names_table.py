import sqlite3

def create_names_table():
    conn = sqlite3.connect('game_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS names (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_names_table()
