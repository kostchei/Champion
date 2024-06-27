import sqlite3
import json
import os
import sys
from contextlib import closing
import logging
import pygame as pg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Pygame
pg.init()

# Constants
BUTTON_PADDING = 20
COLORS = {
    "button": (240, 240, 230),
    "button_hover": (237, 243, 252),
    "button_text": (30, 40, 50),
    "background": (247, 246, 237),
    "button_shadow": (200, 200, 180),
    "popup": (255, 255, 255),
    "popup_border": (0, 0, 0),
}
FONT = pg.font.SysFont('Arial', 24)
POPUP_FONT = pg.font.SysFont('Arial', 20)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

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
                SELECT name, gender, game_editions, race, class, background, strength, intelligence, wisdom, dexterity, constitution, charisma 
                FROM characters WHERE id=?
            ''', (character_id,))
            return cursor.fetchone()

def display_character_data(screen, character_data):
    """ Display character data on the screen """
    screen.fill(COLORS['background'])
    
    # Display top bar with character summary
    summary_text = f"Name: {character_data['name']} | Gender: {character_data['gender']} | Game Editions: {', '.join(character_data['game_editions'])} | Race: {character_data['race']} | Class: {character_data['class']} | Background: {character_data['background']}"
    summary_surface = FONT.render(summary_text, True, COLORS['button_text'])
    screen.blit(summary_surface, (20, 20))

    # Display tabs and pages
    tab_labels = ['Stats', 'Inventory', 'Abilities', 'Notes']
    tab_rects = []
    tab_width = 120
    tab_height = 40

    for i, label in enumerate(tab_labels):
        tab_rect = pg.Rect(10, 100 + i * (tab_height + 10), tab_width, tab_height)
        tab_rects.append(tab_rect)
        pg.draw.rect(screen, COLORS['button'], tab_rect)
        tab_surface = FONT.render(label, True, COLORS['button_text'])
        screen.blit(tab_surface, (tab_rect.x + 10, tab_rect.y + 10))

    # Display content for the first tab (Stats)
    stats = {
        "Strength": character_data['strength'],
        "Intelligence": character_data['intelligence'],
        "Wisdom": character_data['wisdom'],
        "Dexterity": character_data['dexterity'],
        "Constitution": character_data['constitution'],
        "Charisma": character_data['charisma']
    }
    start_y = 100
    for stat, value in stats.items():
        stat_text = f"{stat}: {value}"
        stat_surface = FONT.render(stat_text, True, COLORS['button_text'])
        screen.blit(stat_surface, (150, start_y))
        start_y += 40

    pg.display.flip()

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
        "strength": character_data[6],
        "intelligence": character_data[7],
        "wisdom": character_data[8],
        "dexterity": character_data[9],
        "constitution": character_data[10],
        "charisma": character_data[11]
    }

    # Initialize Pygame screen
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Character Display")

    # Main loop
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        display_character_data(screen, character_data)

    pg.quit()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python csdisplay.py <character_id>")
        sys.exit(1)

    character_id = int(sys.argv[1])
    main(character_id)
