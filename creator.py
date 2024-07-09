import sqlite3
import json
import os
import sys
import random
from contextlib import closing
import logging
import subprocess

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

def roll_stat():
    """ Roll 4d6 and drop the lowest die. """
    rolls = [random.randint(1, 6) for _ in range(4)]
    rolls.remove(min(rolls))
    return sum(rolls)

def calculate_stats():
    """ Calculate the character's stats ensuring total is at least 75. """
    stats = [roll_stat() for _ in range(6)]
    while sum(stats) < 75:
        stats = [roll_stat() for _ in range(6)]
    return {
        "Strength": stats[0],
        "Intelligence": stats[1],
        "Wisdom": stats[2],
        "Dexterity": stats[3],
        "Constitution": stats[4],
        "Charisma": stats[5]
    }

def fetch_character_data(character_id):
    """ Fetch character data from the database using the character ID. """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                SELECT name, gender, game_editions, race, class, background 
                FROM temporary_characters WHERE id=?
            ''', (character_id,))
            return cursor.fetchone()

def fetch_class_details(class_name):
    """ Fetch class details from the database using the class name. """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                SELECT primary_stat, secondary_stat, tertiary_stat, dump_stat 
                FROM classes WHERE name=?
            ''', (class_name,))
            return cursor.fetchone()

def adjust_stats_for_class(stats, class_details):
    """ Adjust stats based on the class details. """
    primary_stat = class_details[0]
    secondary_stat = class_details[1]
    tertiary_stat = class_details[2]
    dump_stat = class_details[3]

    # Convert to title case to match keys in stats dictionary
    primary_stat = primary_stat.title()
    secondary_stat = secondary_stat.title()
    tertiary_stat = tertiary_stat.title()
    dump_stat = dump_stat.title()

    # Ensure primary stat is at least 15
    if stats[primary_stat] < 15:
        stats[primary_stat] = 15

    # Ensure secondary or tertiary stat is at least 13
    if stats[secondary_stat] < 13 and stats[tertiary_stat] < 13:
        stats[secondary_stat] = 13

    # Ensure no stat is below 6 except dump stat
    for stat in stats:
        if stat != dump_stat and stats[stat] < 6:
            stats[stat] = 6

    return stats

def save_character(character_data, stats, saves):
    """ Save the finalized character data to the database. """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                INSERT INTO characters 
                (name, gender, game_editions, race, class, background, strength, intelligence, wisdom, dexterity, constitution, charisma, experience_points, skillProficiencies, languageProficiencies, expertise, craftingTools, vehicles, saves) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                character_data["name"],
                character_data["gender"],
                json.dumps(character_data["game_editions"]),
                character_data["race"],
                character_data["class"],
                character_data["background"],
                stats["Strength"],
                stats["Intelligence"],
                stats["Wisdom"],
                stats["Dexterity"],
                stats["Constitution"],
                stats["Charisma"],
                0,  # Set experience points to zero
                json.dumps(character_data.get("skillProficiencies", [])),
                json.dumps(character_data.get("languageProficiencies", [])),
                json.dumps(character_data.get("expertise", [])),
                json.dumps(character_data.get("craftingTools", [])),
                json.dumps(character_data.get("vehicles", [])),
                json.dumps(saves)
            ))
            character_id = cursor.lastrowid
            conn.commit()
    return character_id

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
        "skillProficiencies": [],
        "languageProficiencies": [],
        "expertise": [],
        "craftingTools": [],
        "vehicles": [],
        "saves": []  # Initialize empty saves list
    }

    # Check if the class contains "Sidekick"
    if "Sidekick" in character_data["class"]:
        logger.info(f"Class {character_data['class']} contains 'Sidekick'. Delegating to NPCcreator.py")
        subprocess.run(['python', get_resource_path('NPCcreator.py'), character_data["class"]])
        return

    # Calculate the character's stats
    stats = calculate_stats()

    # Fetch class details
    class_details = fetch_class_details(character_data["class"])
    if not class_details:
        logger.error(f"No class details found for class {character_data['class']}")
        return

    # Adjust stats based on class details
    stats = adjust_stats_for_class(stats, class_details)

    # Add primary and secondary stats to saves
    saves = [class_details[0].title(), class_details[1].title()]

    # Print progress
    logger.info(f"Character Data: {character_data}")
    logger.info(f"Calculated Stats: {stats}")
    logger.info(f"Initial Saves: {saves}")

    # Save the character data with stats
    character_id = save_character(character_data, stats, saves)

    # Call csdisplay.py to display the character data
    logger.info(f"Displaying character {character_data['name']} with stats {stats}.")
    subprocess.run(['python', get_resource_path('csdisplay.py'), str(character_id)])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python creator.py <character_id>")
        sys.exit(1)

    character_id = int(sys.argv[1])
    main(character_id)
