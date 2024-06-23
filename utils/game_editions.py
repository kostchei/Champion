import sqlite3

def get_db_connection():
    """
    Create a connection to the database.

    Returns:
        sqlite3.Connection: The connection object.
    """
    db_path = './tables/game_database.db'  # Adjust the path to your database
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def get_active_game_editions():
    """
    Fetch the list of active game editions from the database.

    Returns:
        dict: A dictionary mapping edition names to their IDs.
    """
    conn = get_db_connection()
    if not conn:
        return {}

    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM GameEditions")
    editions = cursor.fetchall()
    conn.close()
    return {edition['name']: edition['id'] for edition in editions}
