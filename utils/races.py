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

def check_table_exists(conn, table_name):
    """
    Check if a table exists in the database.

    Args:
        conn (sqlite3.Connection): The connection object.
        table_name (str): The name of the table to check.

    Returns:
        bool: True if the table exists, False otherwise.
    """
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    result = cursor.fetchone()
    return result is not None

def get_races():
    """
    Fetch the list of all races from the database.

    Returns:
        list: A list of race names.
    """
    conn = get_db_connection()
    if not conn:
        return []

    if not check_table_exists(conn, 'lineages'):
        print("Table 'lineages' does not exist.")
        conn.close()
        return []

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM lineages")
    races = cursor.fetchall()
    conn.close()
    return [race['name'] for race in races]

def get_race_details(race_name):
    """
    Get the details of a specific race from the database.

    Args:
        race_name (str): The name of the race to get details for.

    Returns:
        dict: A dictionary containing the details of the race.
    """
    conn = get_db_connection()
    if not conn:
        return {}

    if not check_table_exists(conn, 'lineages'):
        print("Table 'lineages' does not exist.")
        conn.close()
        return {}

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lineages WHERE name = ?", (race_name,))
    race_details = cursor.fetchone()
    conn.close()
    return dict(race_details) if race_details else {}

def get_races_for_editions(game_edition_ids):
    """
    Fetch the list of races available for the given game editions from the database.

    Args:
        game_edition_ids (list): A list of game edition IDs.

    Returns:
        list: A list of race names.
    """
    conn = get_db_connection()
    if not conn:
        return []

    if not check_table_exists(conn, 'lineages'):
        print("Table 'lineages' does not exist.")
        conn.close()
        return []

    cursor = conn.cursor()
    placeholder = ', '.join('?' for _ in game_edition_ids)
    query = f"SELECT name FROM lineages WHERE game_edition_id IN ({placeholder})"
    print(f"Executing query: {query} with values: {game_edition_ids}")  # Debug statement
    cursor.execute(query, game_edition_ids)
    races = cursor.fetchall()
    print(f"Query result: {races}")  # Debug statement
    conn.close()
    return [race['name'] for race in races]

# Example usage
if __name__ == "__main__":
    print(get_races())  # Test function
    print(get_race_details("Elf"))  # Test function
    print(get_races_for_editions([5, 9]))  # Test function
