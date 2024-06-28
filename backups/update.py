import sqlite3
from contextlib import closing
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the correct path for the database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'game_database.db')

# Print the database path for debugging purposes
logger.info(f"Database path: {DB_PATH}")

# Mapping of shorthand stat names to full names
stat_mapping = {
    "str": "Strength",
    "dex": "Dexterity",
    "con": "Constitution",
    "int": "Intelligence",
    "wis": "Wisdom",
    "cha": "Charisma"
}

def update_stat_names():
    """ Update stat names in the classes table. """
    if not os.path.exists(DB_PATH):
        logger.error(f"Database file does not exist at path: {DB_PATH}")
        return

    try:
        with closing(sqlite3.connect(DB_PATH)) as conn:
            with closing(conn.cursor()) as cursor:
                for short_stat, full_stat in stat_mapping.items():
                    cursor.execute('''
                        UPDATE classes 
                        SET primary_stat = CASE WHEN primary_stat = ? THEN ? ELSE primary_stat END,
                            secondary_stat = CASE WHEN secondary_stat = ? THEN ? ELSE secondary_stat END,
                            tertiary_stat = CASE WHEN tertiary_stat = ? THEN ? ELSE tertiary_stat END,
                            dump_stat = CASE WHEN dump_stat = ? THEN ? ELSE dump_stat END
                    ''', (short_stat, full_stat, short_stat, full_stat, short_stat, full_stat, short_stat, full_stat))
                conn.commit()
                logger.info("Stat names updated successfully.")
    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")

if __name__ == "__main__":
    update_stat_names()
