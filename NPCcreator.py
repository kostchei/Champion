import sqlite3
import random
from contextlib import closing
import logging
import os
import json
import sys

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
    """ Roll 5d4-2 for a stat. """
    rolls = [random.randint(1, 4) for _ in range(5)]
    return sum(rolls) - 2

def calculate_stats():
    """ Calculate the NPC's stats. """
    stats = { "Strength": roll_stat(), "Intelligence": roll_stat(), "Wisdom": roll_stat(), 
              "Dexterity": roll_stat(), "Constitution": roll_stat(), "Charisma": roll_stat() }
    return stats

def fetch_class_details(class_name):
    """ Fetch class details from the database using the class name. """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                SELECT primary_stat, dump_stat 
                FROM classes WHERE name=?
            ''', (class_name,))
            return cursor.fetchone()

def assign_primary_and_dump(stats, class_details):
    """ Assign primary and dump stats based on random chance. """
    primary_stat = class_details[0]
    dump_stat = class_details[1]
    
    # 50% chance to assign highest stat to primary_stat
    if random.random() < 0.5:
        highest_stat = max(stats, key=stats.get)
        stats[highest_stat], stats[primary_stat] = stats[primary_stat], stats[highest_stat]

    # 50% chance to assign lowest stat to dump_stat
    if random.random() < 0.5:
        lowest_stat = min(stats, key=stats.get)
        stats[lowest_stat], stats[dump_stat] = stats[dump_stat], stats[lowest_stat]

    return stats

def save_npc_to_characters(class_name, stats):
    """ Save the generated NPC stats to the characters table. """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                INSERT INTO characters 
                (name, gender, game_editions, race, class, background, strength, intelligence, wisdom, dexterity, constitution, charisma) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                "NPC",
                "Unknown",
                json.dumps(["None"]),
                "Unknown",
                class_name,
                "None",
                stats["Strength"],
                stats["Intelligence"],
                stats["Wisdom"],
                stats["Dexterity"],
                stats["Constitution"],
                stats["Charisma"]
            ))
            conn.commit()

def main(class_name):
    # Calculate the NPC's stats
    stats = calculate_stats()
    print(f"Calculated Stats: {stats}")

    # Fetch class details
    class_details = fetch_class_details(class_name)
    if not class_details:
        logger.error(f"No class details found for class {class_name}")
        return
    print(f"Class Details: {class_details}")

    # Assign primary and dump stats based on random chance
    stats = assign_primary_and_dump(stats, class_details)
    print(f"Adjusted Stats: {stats}")

    # Save the NPC stats to the characters table
    save_npc_to_characters(class_name, stats)

    # Log the action
    logger.info(f"NPC with class {class_name} and stats {stats} saved successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python NPCcreator.py <class_name>")
        sys.exit(1)

    class_name = sys.argv[1]
    main(class_name)