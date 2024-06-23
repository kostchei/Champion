# utils/classes.py

import sqlite3

def get_classes(active_editions):
    """
    Load the list of class names from the database based on active game editions.

    Args:
        active_editions (list): A list of active game edition names.

    Returns:
        list: A list of class names.
    """
    db_path = './tables/game_database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch the IDs of the active editions
    placeholders = ', '.join('?' for _ in active_editions)
    query = f'SELECT id FROM GameEditions WHERE name IN ({placeholders})'
    cursor.execute(query, active_editions)
    active_edition_ids = [row[0] for row in cursor.fetchall()]
    
    if not active_edition_ids:
        conn.close()
        return []

    placeholders = ', '.join('?' for _ in active_edition_ids)
    query = f'SELECT name FROM Classes WHERE game_edition IN ({placeholders})'
    cursor.execute(query, active_edition_ids)
    classes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return classes

def get_class_details(class_name):
    """
    Get the details of a specific class from the database.

    Args:
        class_name (str): The name of the class to get details for.

    Returns:
        dict: A dictionary containing the details of the class.
    """
    db_path = './tables/game_database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Classes WHERE name = ?', (class_name,))
    class_details = cursor.fetchone()
    conn.close()

    if class_details:
        details = {
            "name": class_details[1],
            "primary_stat": class_details[2],
            "secondary_stat": class_details[3],
            "proficiency": class_details[4],
            "armor_proficiencies": class_details[5],
            "weapon_proficiencies": class_details[6],
            "skill_proficiencies": class_details[7],
            "starting_equipment": class_details[8],
            "tertiary_stat": class_details[9]
        }
        return details
    else:
        return {}
