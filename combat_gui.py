import json
import sys
import pygame as pg
from collections import Counter

# Initialize Pygame
pg.init()
pg.font.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
BUTTON_WIDTH, BUTTON_HEIGHT = 250, 60
BUTTON_PADDING = 20
BUTTON_COLOR = (240, 240, 230)  # GREY
BUTTON_HOVER_COLOR = (237, 243, 252)  # WHITE
BUTTON_TEXT_COLOR = (30, 40, 50)  # DARK_BLUE
BACKGROUND_COLOR = (247, 246, 237)  # BUFF_OFF_WHITE
BUTTON_SHADOW_COLOR = (200, 200, 180)  # Light brown shadow (not provided, derived for shadow)
FONT = pg.font.SysFont('Arial', 18)  # Smaller font

# Set up the screen
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Combat GUI")

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return {}

def draw_text(screen, text, position, font, color=(0, 0, 0)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def draw_button(text, position):
    mouse_pos = pg.mouse.get_pos()
    button_rect = pg.Rect(position[0], position[1], BUTTON_WIDTH, BUTTON_HEIGHT)
    shadow_rect = pg.Rect(position[0] + 5, position[1] + 5, BUTTON_WIDTH, BUTTON_HEIGHT)
    color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR

    pg.draw.rect(screen, BUTTON_SHADOW_COLOR, shadow_rect, border_radius=10)  # Shadow
    pg.draw.rect(screen, color, button_rect, border_radius=10)  # Button
    pg.draw.rect(screen, (0, 0, 0), button_rect, 2, border_radius=10)  # Border

    text_surface = FONT.render(text, True, BUTTON_TEXT_COLOR)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)

    return button_rect

def draw_columns(screen, columns, font):
    for col in columns:
        x, y = col['position']
        for line in col['content']:
            draw_text(screen, line, (x, y), font)
            y += font.get_linesize()

def combat_loop(player_data, encounter_data):
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Combat GUI")

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOR)  # Buff Off White background

        # Draw top bar buttons
        top_buttons = ["Attack", "Bells", "Weather", "Features"]
        for i, button_text in enumerate(top_buttons):
            draw_button(button_text, (i * (BUTTON_WIDTH + BUTTON_PADDING), 0))

        # Draw bottom bar buttons
        bottom_buttons = ["Loot", "Morale Check", "Flee"]
        for i, button_text in enumerate(bottom_buttons):
            draw_button(button_text, (i * (BUTTON_WIDTH + BUTTON_PADDING), SCREEN_HEIGHT - BUTTON_HEIGHT))

        # Define column positions
        column_width = SCREEN_WIDTH // 6
        column_positions = [i * column_width for i in range(6)]
        font_linesize = FONT.get_linesize()

        # Prepare content for columns
        columns = [
            {'position': (column_positions[0], 100), 'content': []},
            {'position': (column_positions[1], 100), 'content': []},
            {'position': (column_positions[2], 100), 'content': []},
            {'position': (column_positions[3], 100), 'content': []},
            {'position': (column_positions[4], 100), 'content': []},
            {'position': (column_positions[5], 100), 'content': []},
        ]

        # Add player data to columns 1 and 2
        columns[0]['content'].append(f"Player: {player_data['name']}")
        columns[0]['content'].append(f"HP: {player_data['hit_points']}")

        # Add encounter details to column 3
        columns[2]['content'].append(f"Difficulty: {encounter_data['difficulty']}")
        columns[2]['content'].append(f"XP Budget: {encounter_data['xp_budget']}")

        # Count monsters and prepare content for columns 4 and 5
        monsters_data = encounter_data['encounter']
        monster_counts = Counter(monster['name'] for monster in monsters_data)
        
        for idx, (monster_name, count) in enumerate(monster_counts.items()):
            monster_info = next(monster for monster in monsters_data if monster['name'] == monster_name)
            column_index = 3 if idx % 2 == 0 else 4
            columns[column_index]['content'].append(f"Monster {idx + 1}: {monster_name} x{count}")
            columns[column_index]['content'].append(f"Size: {monster_info.get('size', 'N/A')}")
            columns[column_index]['content'].append(f"Type: {monster_info.get('type', 'N/A')}")
            columns[column_index]['content'].append(f"Alignment: {', '.join(monster_info.get('alignment', ['N/A']))}")
            columns[column_index]['content'].append(f"HP: {monster_info.get('hp', {}).get('average', 'N/A')} ({monster_info.get('hp', {}).get('formula', 'N/A')})")
            columns[column_index]['content'].append(f"AC: {monster_info.get('ac', 'N/A')}")
            columns[column_index]['content'].append(f"Speed: {monster_info.get('speed', {}).get('walk', 'N/A')} ft.")
            columns[column_index]['content'].append(f"CR: {monster_info.get('cr', 'N/A')}")
            columns[column_index]['content'].append(f"STR: {monster_info.get('str', 'N/A')}")
            columns[column_index]['content'].append(f"DEX: {monster_info.get('dex', 'N/A')}")
            columns[column_index]['content'].append(f"CON: {monster_info.get('con', 'N/A')}")
            columns[column_index]['content'].append(f"INT: {monster_info.get('int', 'N/A')}")
            columns[column_index]['content'].append(f"WIS: {monster_info.get('wis', 'N/A')}")
            columns[column_index]['content'].append(f"CHA: {monster_info.get('cha', 'N/A')}")
            columns[column_index]['content'].append(f"Actions:")
            actions = monster_info.get('action', [])
            for action in actions:
                columns[column_index]['content'].append(f"- {action}")

        # Draw all columns
        draw_columns(screen, columns, FONT)

        pg.display.flip()

if __name__ == "__main__":
    # Load encounter data from JSON file specified as a command-line argument
    encounter_file = sys.argv[1]
    encounter_data = load_json(encounter_file)

    # Example player data (hardcoded for now)
    player_data = {
        "name": "Player 1",  # Hardcoded; replace with actual player data if available
        "hit_points": 100,   # Hardcoded; replace with actual player hit points if available
    }

    # Run the combat loop
    combat_loop(player_data, encounter_data)
