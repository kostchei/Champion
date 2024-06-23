import sqlite3

def get_db_connection():
    db_path = './tables/game_database.db'
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def get_active_game_editions():
    conn = get_db_connection()
    if not conn:
        return {}
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM GameEditions")
    editions = cursor.fetchall()
    conn.close()
    return {edition['name']: edition['id'] for edition in editions}
