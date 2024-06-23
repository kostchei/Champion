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

def get_backgrounds():
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM backgrounds")
    backgrounds = cursor.fetchall()
    conn.close()
    return [background['name'] for background in backgrounds]

def get_background_details(background_name):
    conn = get_db_connection()
    if not conn:
        return {}

    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, skillProficiencies, languageProficiencies, startingEquipment, entries, campaign_specific
        FROM backgrounds
        WHERE name = ?
    """, (background_name,))
    background_details = cursor.fetchone()
    conn.close()
    return dict(background_details) if background_details else {}
