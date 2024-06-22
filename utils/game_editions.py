import sqlite3
import os

def get_active_game_editions():
    # Get the absolute path to the database
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, '..', 'tables', 'game_database.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM GameEditions WHERE active = 1')
    editions = [row[0] for row in cursor.fetchall()]
    conn.close()
    return editions
