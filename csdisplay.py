import sqlite3
import json
import os
import sys
from contextlib import closing
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_resource_path(relative_path):
    """ Get the absolute path to the resource, works for both development and PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Set the correct path for the database
DB_PATH = get_resource_path(os.path.join('tables', 'game_database.db'))

def fetch_character_data(character_id):
    """ Fetch finalized character data from the database using the character ID. """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                SELECT name, gender, game_editions, race, class, background, stats 
                FROM characters WHERE id=?
            ''', (character_id,))
            return cursor.fetchone()

def main(character_id):
    # Fetch the character data
    character_data = fetch_character_data(character_id)
    if not character_data:
        logger.error(f"No character found with ID {character_id}")
        return

    # Unpack character data
    character_data = {
        "name": character_data[0],
        "gender": character_data[1],
        "game_editions": json.loads(character_data[2]),
        "race": character_data[3],
        "class": character_data[4],
        "background": character_data[5],
        "stats": json.loads(character_data[6])
    }

    # Print character data
    print(f"Name: {character_data['name']}")
    print(f"Gender: {character_data['gender']}")
    print(f"Game Editions: {', '.join(character_data['game_editions'])}")
    print(f"Race: {character_data['race']}")
    print(f"Class: {character_data['class']}")
    print(f"Background: {character_data['background']}")
    print("Stats:")
    for stat, value in character_data['stats'].items():
        print(f"  {stat}: {value}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python csdisplay.py <character_id>")
        sys.exit(1)

    character_id = int(sys.argv[1])
    main(character_id)
