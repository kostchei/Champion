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
BOTTOM_BUTTON_SIZE = (200, 40)
BOTTOM_BUTTON_PADDING = 20
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

def load_menu_options(menu_name):
    file_path = os.path.join('menu_options', f'{menu_name}.json')
    return load_json(file_path).get('options', [])

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

def draw_button(text, position, size):
    mouse_pos = pg.mouse.get_pos()
    button_rect = pg.Rect(*position, *size)
    shadow_rect = pg.Rect(position[0] + 5, position[1] + 5, *size)
    color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR

    pg.draw.rect(screen, BUTTON_SHADOW_COLOR, shadow_rect, border_radius=10)  # Shadow
    pg.draw.rect(screen, color, button_rect, border_radius=10)  # Button
    pg.draw.rect(screen, (0, 0, 0), button_rect, 2, border_radius=10)  # Border

    text_surface = FONT.render(text, True, BUTTON_TEXT_COLOR)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)
    return button_rect

def draw_columns(screen, columns, font, column_width, scroll_offsets):
    for col, offset in zip(columns, scroll_offsets):
        x, y = col['position']
        y += offset
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

def draw_pull_up_menu(options, position):
    menu_rects = []
    menu_width, menu_height = 200, 40 * len(options)
    menu_rect = pg.Rect(position[0], position[1] - menu_height, menu_width, menu_height)
    pg.draw.rect(screen, BUTTON_COLOR, menu_rect, border_radius=10)
    pg.draw.rect(screen, (0, 0, 0), menu_rect, 2, border_radius=10)

    for i, option in enumerate(options):
        option_rect = pg.Rect(position[0], position[1] - (i + 1) * 40, menu_width, 40)
        pg.draw.rect(screen, BUTTON_COLOR, option_rect, border_radius=10)
        text_surface = FONT.render(option, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=option_rect.center)
        screen.blit(text_surface, text_rect)
        menu_rects.append((option_rect, option))

    return menu_rects

def invoke_script(option):
    script_path = f"./utils/{option.lower().replace(' ', '_')}.py"
    result = os.popen(f"python {script_path}").read()
    return result

def update_log(result, columns):
    columns[2]['content'].append(result)

def combat_loop(player_data, encounter_data):
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Combat GUI")

    column_scroll_offsets = [0, 0, 0, 0, 0]  # Initial scroll offsets for each column
    column_height = SCREEN_HEIGHT - 200  # Subtracting some space for buttons

    active_menu = None
    active_button = None
    menu_rects = []

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if active_menu:
                    for rect, option in menu_rects:
                        if rect.collidepoint(event.pos):
                            result = invoke_script(option)
                            update_log(result, columns)
                            active_menu = None
                            break
                else:
                    if event.button in (4, 5):  # Mouse wheel scroll up or down
                        mouse_x, mouse_y = event.pos
                        column_width = (SCREEN_WIDTH * 0.8) // 5
                        column_positions = [int(SCREEN_WIDTH * 0.1) + i * column_width for i in range(5)]
                        for i, x in enumerate(column_positions):
                            if x <= mouse_x < x + column_width:
                                scroll_direction = -1 if event.button == 4 else 1
                                column_scroll_offsets[i] += scroll_direction * 30
                                column_scroll_offsets[i] = max(min(column_scroll_offsets[i], 0), -column_height)
                    else:
                        buttons = ["1.Move", "2.Action", "3.Bonus", "4.Reaction", "5.Free Action", "6.Spellbook", "7.Complete"]
                        total_width = len(buttons) * (BOTTOM_BUTTON_SIZE[0] + BOTTOM_BUTTON_PADDING) - BOTTOM_BUTTON_PADDING
                        start_x = (SCREEN_WIDTH - total_width) // 2
                        for i, text in enumerate(buttons):
                            button_rect = draw_button(text, (start_x + i * (BOTTOM_BUTTON_SIZE[0] + BOTTOM_BUTTON_PADDING), SCREEN_HEIGHT - BOTTOM_BUTTON_SIZE[1] - 20), BOTTOM_BUTTON_SIZE)
                            if button_rect.collidepoint(event.pos):
                                active_button = text.split('.')[0].lower()
                                active_menu = load_menu_options(f'c{active_button}')
                                menu_rects = draw_pull_up_menu(active_menu, (start_x + i * (BOTTOM_BUTTON_SIZE[0] + BOTTOM_BUTTON_PADDING), SCREEN_HEIGHT - BOTTOM_BUTTON_SIZE[1] - 20))
                                break

        screen.fill(BACKGROUND_COLOR)

        if active_menu:
            menu_rects = draw_pull_up_menu(active_menu, (start_x + int(active_button) * (BOTTOM_BUTTON_SIZE[0] + BOTTOM_BUTTON_PADDING), SCREEN_HEIGHT - BOTTOM_BUTTON_SIZE[1] - 20))

        # Draw bottom buttons centered
        buttons = ["1.Move", "2.Action", "3.Bonus", "4.Reaction", "5.Free Action", "6.Spellbook", "7.Complete"]
        total_width = len(buttons) * (BOTTOM_BUTTON_SIZE[0] + BOTTOM_BUTTON_PADDING) - BOTTOM_BUTTON_PADDING
        start_x = (SCREEN_WIDTH - total_width) // 2
        for i, text in enumerate(buttons):
            draw_button(text, (start_x + i * (BOTTOM_BUTTON_SIZE[0] + BOTTOM_BUTTON_PADDING), SCREEN_HEIGHT - BOTTOM_BUTTON_SIZE[1] - 20), BOTTOM_BUTTON_SIZE)

        # Define column positions
        column_width = (SCREEN_WIDTH * 0.8) // 5
        column_positions = [int(SCREEN_WIDTH * 0.1) + i * column_width for i in range(5)]

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

        # Additional player data to column 2 if overflowing from column 1
        if len(player_content) > column_height // FONT.get_height():
            columns[1]['content'].extend(player_content[column_height // FONT.get_height():])
            player_content = player_content[:column_height // FONT.get_height()]

        # Encounter details in column 3 (log)
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

        draw_columns(screen, columns, FONT, column_width, column_scroll_offsets)
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
