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
BUTTON_SIZE = (250, 60)
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
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def draw_text(screen, text, position, font, color=(0, 0, 0), max_width=None):
    words = text.split(' ')
    space_width, _ = font.size(' ')
    x, y = position
    for word in words:
        word_surface = font.render(word, True, color)
        word_width, word_height = word_surface.get_size()
        if max_width and x + word_width >= max_width:
            x, y = position[0], y + word_height
        screen.blit(word_surface, (x, y))
        x += word_width + space_width
    return y + word_height

def draw_button(text, position):
    mouse_pos = pg.mouse.get_pos()
    button_rect = pg.Rect(*position, *BUTTON_SIZE)
    shadow_rect = pg.Rect(position[0] + 5, position[1] + 5, *BUTTON_SIZE)
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
    value = data.get(key, 'N/A')
    if isinstance(value, list):
        return ', '.join(map(str, value))
    elif isinstance(value, dict):
        return ', '.join(f"{k}: {v}" for k, v in value.items())
    return str(value)

def find_latest_character_file(realm):
    realm_files = [f for f in glob('./saves/*.json') if f.endswith(f'.{realm}.json')]
    return max(realm_files, key=os.path.getctime) if realm_files else None

def load_character_data(realm):
    latest_file = find_latest_character_file(realm)
    return load_json(latest_file) if latest_file else {}

def combat_loop(player_data, encounter_data):
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Combat GUI")

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOR)

        # Draw top and bottom buttons centered
        buttons = [("Initiative", "Hour", "Skies", "Scape"), ("Engage", "Morale", "Loot", "Flee")]
        for y, button_list in zip([0, SCREEN_HEIGHT - BUTTON_SIZE[1]], buttons):
            total_width = len(button_list) * (BUTTON_SIZE[0] + BUTTON_PADDING) - BUTTON_PADDING
            start_x = (SCREEN_WIDTH - total_width) // 2
            for i, text in enumerate(button_list):
                draw_button(text, (start_x + i * (BUTTON_SIZE[0] + BUTTON_PADDING), y))

        # Define column positions
        column_width = SCREEN_WIDTH // 6
        column_positions = [i * column_width for i in range(6)]

        # Prepare content for columns
        columns = [{'position': (x, 100), 'content': []} for x in column_positions]

        # Add player data to column 1
        player_content = columns[0]['content']
        player_content.extend([
            f"HP: {player_data.get('hit_points', 'N/A')}",
            f"Current HP: {player_data.get('current_hp', 'N/A')}",
            f"Class: {player_data.get('class', 'N/A')}",
            f"AC: {player_data.get('armor_class', 'N/A')}",
            f"Dexterity Bonus: {player_data.get('dexterity_modifier', 'N/A')}",
            f"Speed: {player_data.get('speed', 'N/A')}",
            "Skills:"
        ])

        skill_fields = [
            'athletics_bonus', 'arcana_bonus', 'history_bonus', 'investigation_bonus',
            'nature_bonus', 'religion_bonus', 'animal_handling_bonus', 'insight_bonus',
            'medicine_bonus', 'perception_bonus', 'survival_bonus', 'acrobatics_bonus',
            'sleight_of_hand_bonus', 'stealth_bonus', 'deception_bonus', 'intimidation_bonus',
            'performance_bonus', 'persuasion_bonus'
        ]
        for skill in player_data.get('skills', []):
            player_content.append(f"  {skill}")

        for skill_field in skill_fields:
            if skill_field in player_data:
                player_content.append(f"  {skill_field.replace('_bonus', '').replace('_', ' ').capitalize()}: {player_data[skill_field]}")

        # Saving Throws
        player_content.append("Saving Throws:")
        saving_throws_dict = {
            "Str Save": "strength", "Int Save": "intelligence", "Wis Save": "wisdom",
            "Dex Save": "dexterity", "Con Save": "constitution", "Cha Save": "charisma"
        }
        for save, attr in saving_throws_dict.items():
            save_bonus = player_data.get(f"{save.lower().replace(' ', '_')}_bonus", 'N/A')
            player_content.append(f"  {save}: {save_bonus}")

        # Features
        player_content.append("Features:")
        for feature_name, feature in player_data.get('features', {}).items():
            player_content.append(f"{feature_name}: {feature.get('description', 'N/A')}")

        # Fighting Style
        chosen_fighting_style = player_data.get('chosen_fighting_style', {})
        if chosen_fighting_style:
            player_content.append(f"Chosen Fighting Style: {chosen_fighting_style.get('name', 'N/A')}")
            player_content.append(f"  {chosen_fighting_style.get('description', 'N/A')}")

        # Attacks
        if 'attack' in player_data:
            attack = player_data['attack']
            player_content.extend([
                "Attack:",
                f"  Name: {attack.get('name', 'N/A')}",
                f"  To Hit: {attack.get('to_hit', 'N/A')}",
                f"  Damage: {attack.get('damage', 'N/A')}"
            ])

        # Encounter details in column 3
        encounter_content = columns[2]['content']
        encounter_content.extend([
            f"Difficulty: {encounter_data['difficulty']}",
            f"XP Budget: {encounter_data['xp_budget']}"
        ])

        # Monsters in columns 4 and 5
        monsters_data = encounter_data['encounter']
        monster_counts = Counter(monster['name'] for monster in monsters_data)
        fields_of_interest = [
            "name", "size", "type", "alignment", "ac", "hp", "speed", "str", "dex", "con", "int", "wis", "cha",
            "skill", "senses", "cr", "immune", "vulnerable", "conditionImmune", "trait", "action", "reaction", "spellcasting"
        ]
        for idx, (monster_name, count) in enumerate(monster_counts.items()):
            monster_info = next(monster for monster in monsters_data if monster['name'] == monster_name)
            column_index = 3 if idx % 2 == 0 else 4
            monster_content = columns[column_index]['content']
            monster_content.append(f"Monster {idx + 1}: {monster_name} x{count}")
            for key in fields_of_interest:
                if key != "name":
                    value = get_field_value(monster_info, key)
                    monster_content.append(f"{key.capitalize()}: {value}")

        draw_columns(screen, columns, FONT, column_width)
        pg.display.flip()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python combat_gui.py <encounter_file> <realm>")
        sys.exit(1)

    encounter_file = sys.argv[1]
    realm = sys.argv[2]
    
    encounter_data = load_json(encounter_file)
    player_data = load_character_data(realm)

    print(f"Loaded character data for realm '{realm}': {player_data}")

    combat_loop(player_data, encounter_data)
