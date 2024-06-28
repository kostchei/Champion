import sqlite3
from contextlib import closing

def get_db_connection():
    """ Get a database connection. """
    db_path = './tables/game_database.db'
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def fetch_available_languages():
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM languages")
    languages = cursor.fetchall()
    conn.close()
    return [language['name'] for language in languages]

def get_stat_modifier(stat_value):
    """ Fetch the modifier for a given stat value from the stat_bonus table. """
    conn = get_db_connection()
    if not conn:
        return 0
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT modifier
        FROM stat_bonus
        WHERE score = ?
    ''', (stat_value,))
    result = cursor.fetchone()
    conn.close()
    
    return result["modifier"] if result else 0

def get_skill_bonus(skill_key, attribute_modifier, proficiency_bonus, primary_stat, secondary_stat):
    """ Calculate the skill bonus. """
    if skill_key in primary_stat or skill_key in secondary_stat:
        return attribute_modifier + proficiency_bonus
    return attribute_modifier
