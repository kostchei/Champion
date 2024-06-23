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

def check_table_exists(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    return cursor.fetchone() is not None

def get_races():
    conn = get_db_connection()
    if not conn or not check_table_exists(conn, 'lineages'):
        return []

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM lineages")
    races = cursor.fetchall()
    conn.close()
    return [race['name'] for race in races]

def get_race_details(race_name):
    conn = get_db_connection()
    if not conn or not check_table_exists(conn, 'lineages'):
        return {}

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lineages WHERE name = ?", (race_name,))
    race_details = cursor.fetchone()
    conn.close()
    return dict(race_details) if race_details else {}

def get_races_for_editions(game_edition_ids):
    conn = get_db_connection()
    if not conn or not check_table_exists(conn, 'lineages'):
        return []

    cursor = conn.cursor()
    placeholder = ', '.join('?' for _ in game_edition_ids)
    query = f"SELECT name FROM lineages WHERE game_edition_id IN ({placeholder})"
    cursor.execute(query, game_edition_ids)
    races = cursor.fetchall()
    conn.close()
    return [race['name'] for race in races]
