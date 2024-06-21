import sqlite3
import random
import os

def get_db_connection():
    # Adjust the path to the database file in the 'tables' directory
    db_path = os.path.join(os.path.dirname(__file__), '..', 'tables', 'game_database.db')
    return sqlite3.connect(db_path)

def get_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM names')
    names = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return names

def get_random_name():
    names = get_names()
    return random.choice(names)


