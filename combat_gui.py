import json
import sys
import os
import pygame as pg
from collections import Counter
from glob import glob

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
FONT = pg.font.SysFont('Arial', 14)  # Reduced font size to 75%

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

def draw_text(screen, text, position, font, color=(0, 0, 0), max_width=None):
    words = text.split(' ')
    space_width, _ = font.size(' ')
    x, y = position
    for word in words:
        word_surface = font.render(word, True, color)
        word_width, word_height = word_surface.get_size()
        if max_width is not None and x + word_width >= max_width:
            x = position[0]  # Reset the x.
            y += word_height  # Start on new row.
        screen.blit(word_surface, (x, y))
        x += word_width + space_width
    return y + word_height

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

def draw_columns(screen, columns, font, column_width):
    for col in columns:
        x, y = col['position']
        for line in col['content']:
            y = draw_text(screen, line, (x, y), font, max_width=x + column_width)

def get_field_value(data, key):
    if key in data:
        value = data[key]
        if isinstance(value, list):
            return ', '.join(map(str, value))
        elif isinstance(value, dict):
            return ', '.join(f"{k}: {v}" for k, v in value.items())
        else:
            return str(value)
    return 'N/A'

def find_latest_character_file(realm):
    save_files = glob('./saves/*.json')
    realm_files = [f for f in save_files if f.endswith(f'.{realm}.json')]
    if not realm_files:
        return None
    latest_file = max(realm_files, key=os.path.getctime)
    return latest_file

def load_character_data(realm):
    latest_file = find_latest_character_file(realm)
    if latest_file:
        return load_json(latest_file)
    return {}

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
        top_buttons = ["Initiative", "Hour", "Skies", "Scape"]
        bottom_buttons = ["Engage", "Morale", "Loot", "Flee"]

        # Calculate the starting x position to center the buttons
        total_button_width = len(top_buttons) * (BUTTON_WIDTH + BUTTON_PADDING) - BUTTON_PADDING
        start_x_top = (SCREEN_WIDTH - total_button_width) // 2
        start_x_bottom = start_x_top

        # Draw top buttons centered
        for i, button_text in enumerate(top_buttons):
            draw_button(button_text, (start_x_top + i * (BUTTON_WIDTH + BUTTON_PADDING), 0))

        # Draw bottom buttons centered
        for i, button_text in enumerate(bottom_buttons):
            draw_button(button_text, (start_x_bottom + i * (BUTTON_WIDTH + BUTTON_PADDING), SCREEN_HEIGHT - BUTTON_HEIGHT))

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
        columns[0]['content'].append(f"Player: {player_data.get('name', 'N/A')}")
        columns[0]['content'].append(f"HP: {player_data.get('hit_points', 'N/A')}")

        # Add character data to column 1
        if player_data:
            columns[0]['content'].append(f"Character: {player_data.get('name', 'N/A')}")
            columns[0]['content'].append(f"Race: {player_data.get('race', 'N/A')}")
            columns[0]['content'].append(f"Class: {player_data.get('class', 'N/A')}")
            columns[0]['content'].append(f"HP: {player_data.get('hit_points', 'N/A')}")
            columns[0]['content'].append(f"AC: {player_data.get('armor_class', 'N/A')}")
            columns[0]['content'].append(f"Speed: {player_data.get('speed', 'N/A')}")

            # Skills and skill bonuses
            columns[0]['content'].append("Skills:")
            skill_fields = ['athletics_bonus', 'arcana_bonus', 'history_bonus', 'investigation_bonus',
                            'nature_bonus', 'religion_bonus', 'animal_handling_bonus', 'insight_bonus',
                            'medicine_bonus', 'perception_bonus', 'survival_bonus', 'acrobatics_bonus',
                            'sleight_of_hand_bonus', 'stealth_bonus', 'deception_bonus', 'intimidation_bonus',
                            'performance_bonus', 'persuasion_bonus']
            for skill in player_data.get('skills', []):
                columns[0]['content'].append(f"  {skill}")

            for skill_field in skill_fields:
                if skill_field in player_data:
                    columns[0]['content'].append(f"  {skill_field.replace('_bonus', '').replace('_', ' ').capitalize()}: {player_data[skill_field]}")

            columns[0]['content'].append("Saving Throws:")
            for save in player_data.get('saving_throws', []):
                columns[0]['content'].append(f"  {save}")

            columns[0]['content'].append("Features:")
            for feature_name, feature in player_data.get('features', {}).items():
                columns[0]['content'].append(f"{feature_name}: {feature.get('description', 'N/A')}")

            chosen_fighting_style = player_data.get('chosen_fighting_style', {})
            if chosen_fighting_style:
                columns[0]['content'].append(f"Chosen Fighting Style: {chosen_fighting_style.get('name', 'N/A')}")
                columns[0]['content'].append(f"  {chosen_fighting_style.get('description', 'N/A')}")

            # Add attacks
            if 'attack' in player_data:
                attack = player_data['attack']
                columns[0]['content'].append("Attack:")
                columns[0]['content'].append(f"  Name: {attack.get('name', 'N/A')}")
                columns[0]['content'].append(f"  To Hit: {attack.get('to_hit', 'N/A')}")
                columns[0]['content'].append(f"  Damage: {attack.get('damage', 'N/A')}")

        # Add encounter details to column 3
        columns[2]['content'].append(f"Difficulty: {encounter_data['difficulty']}")
        columns[2]['content'].append(f"XP Budget: {encounter_data['xp_budget']}")

        # List of fields we are interested in
        fields_of_interest = [
            "name", "size", "type", "alignment", "ac", "hp", "speed", "str", "dex", "con", "int", "wis", "cha",
            "skill", "senses", "cr", "immune", "vulnerable", "conditionImmune", "trait", "action", "reaction", "spellcasting"
        ]

        # Count monsters and prepare content for columns 4 and 5
        monsters_data = encounter_data['encounter']
        monster_counts = Counter(monster['name'] for monster in monsters_data)

        for idx, (monster_name, count) in enumerate(monster_counts.items()):
            monster_info = next(monster for monster in monsters_data if monster['name'] == monster_name)
            column_index = 3 if idx % 2 == 0 else 4
            columns[column_index]['content'].append(f"Monster {idx + 1}: {monster_name} x{count}")

            for key in fields_of_interest:
                if key == "name":
                    continue
                value = get_field_value(monster_info, key)
                columns[column_index]['content'].append(f"{key.capitalize()}: {value}")

        # Draw all columns
        draw_columns(screen, columns, FONT, column_width)

        pg.display.flip()

if __name__ == "__main__":
    # Load encounter data from JSON file specified as a command-line argument
    if len(sys.argv) < 3:
        print("Usage: python combat_gui.py <encounter_file> <realm>")
        sys.exit(1)

    encounter_file = sys.argv[1]
    realm = sys.argv[2]
    
    encounter_data = load_json(encounter_file)

    # Load character data
    player_data = load_character_data(realm)

    # Debugging: Print loaded character data
    print(f"Loaded character data for realm '{realm}': {player_data}")

    # Run the combat loop
    combat_loop(player_data, encounter_data)
