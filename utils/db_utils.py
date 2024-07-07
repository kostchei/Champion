# utils/db_utils.py

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

def fetch_data(table, column, value):
    """ Fetch data from a specific table based on a column and value. """
    conn = get_db_connection()
    if not conn:
        return {}

    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE {column} = ?", (value,))
    data = cursor.fetchone()
    conn.close()
    return dict(data) if data else {}

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

def fetch_character(character_id):
    """ Fetch character data from the database using the character ID. """
    conn = get_db_connection()
    if not conn:
        return {}

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
    data = cursor.fetchone()
    conn.close()
    return dict(data) if data else {}

def fetch_level_and_proficiency_bonus(exp):
    """ Fetch the level and proficiency bonus based on experience points. """
    conn = get_db_connection()
    if not conn:
        return None, None
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT level, proficiency_bonus
        FROM xp_lv_bonus
        WHERE experience_points <= ?
        ORDER BY experience_points DESC
        LIMIT 1
    ''', (exp,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result["level"], result["proficiency_bonus"]
    else:
        return None, None

def update_character_level_and_proficiency(character_id, level, proficiency_bonus):
    """ Update the character's level and proficiency bonus in the database. """
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE characters
        SET level = ?, proficiency_bonus = ?
        WHERE id = ?
    ''', (level, proficiency_bonus, character_id))
    conn.commit()
    conn.close()

def update_character_skills(character_id, skills):
    """ Update the character's skills in the database. """
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute('DELETE FROM character_skills WHERE character_id = ?', (character_id,))
    for skill, value in skills.items():
        cursor.execute('''
            INSERT INTO character_skills (character_id, skill, value)
            VALUES (?, ?, ?)
        ''', (character_id, skill, value))
    conn.commit()
    conn.close()

def update_character_saves(character_id, saves):
    """ Update the character's saves in the database. """
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute('DELETE FROM character_saves WHERE character_id = ?', (character_id,))
    for save, value in saves.items():
        cursor.execute('''
            INSERT INTO character_saves (character_id, save, value)
            VALUES (?, ?, ?)
        ''', (character_id, save, value))
    conn.commit()
    conn.close()

def get_skill_bonus(character_id, skill):
    """ Fetch the bonus for a given skill for a character from the character_skills table. """
    conn = get_db_connection()
    if not conn:
        return 0
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT value
        FROM character_skills
        WHERE character_id = ? AND skill = ?
    ''', (character_id, skill))
    result = cursor.fetchone()
    conn.close()
    
    return result["value"] if result else 0
