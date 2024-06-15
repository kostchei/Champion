import json
import sys
import pygame as pg

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

        # Display player data in columns 1 and 2
        draw_text(screen, f"Player: {player_data['name']}", (column_positions[0] + 20, 100), FONT)
        draw_text(screen, f"HP: {player_data['hit_points']}", (column_positions[0] + 20, 130), FONT)

        # Display encounter details in column 3
        draw_text(screen, f"Difficulty: {encounter_data['difficulty']}", (column_positions[2] + 20, 100), FONT)
        draw_text(screen, f"XP Budget: {encounter_data['xp_budget']}", (column_positions[2] + 20, 130), FONT)

        # Access and display monster data in columns 4 and 5
        monsters_data = encounter_data['encounter']
        for idx, monster in enumerate(monsters_data):
            y_offset = 160 + idx * 420
            x_offset = column_positions[3] + 20
            draw_text(screen, f"Monster {idx + 1}: {monster['name']}", (x_offset, y_offset), FONT)
            draw_text(screen, f"Size: {monster.get('size', 'N/A')}", (x_offset, y_offset + 30), FONT)
            draw_text(screen, f"Type: {monster.get('type', 'N/A')}", (x_offset, y_offset + 60), FONT)
            draw_text(screen, f"Alignment: {', '.join(monster.get('alignment', ['N/A']))}", (x_offset, y_offset + 90), FONT)
            draw_text(screen, f"HP: {monster.get('hp', {}).get('average', 'N/A')} ({monster.get('hp', {}).get('formula', 'N/A')})", (x_offset, y_offset + 120), FONT)
            draw_text(screen, f"AC: {monster.get('ac', 'N/A')}", (x_offset, y_offset + 150), FONT)
            draw_text(screen, f"Speed: {monster.get('speed', {}).get('walk', 'N/A')} ft.", (x_offset, y_offset + 180), FONT)
            draw_text(screen, f"CR: {monster.get('cr', 'N/A')}", (x_offset, y_offset + 210), FONT)
            draw_text(screen, f"STR: {monster.get('str', 'N/A')}", (x_offset, y_offset + 240), FONT)
            draw_text(screen, f"DEX: {monster.get('dex', 'N/A')}", (x_offset, y_offset + 270), FONT)
            draw_text(screen, f"CON: {monster.get('con', 'N/A')}", (x_offset, y_offset + 300), FONT)
            draw_text(screen, f"INT: {monster.get('int', 'N/A')}", (x_offset, y_offset + 330), FONT)
            draw_text(screen, f"WIS: {monster.get('wis', 'N/A')}", (x_offset, y_offset + 360), FONT)
            draw_text(screen, f"CHA: {monster.get('cha', 'N/A')}", (x_offset, y_offset + 390), FONT)
            draw_text(screen, f"Actions:", (x_offset, y_offset + 420), FONT)

            actions = monster.get('action', [])
            for action_idx, action in enumerate(actions):
                draw_text(screen, f"- {action}", (x_offset + 20, y_offset + 450 + action_idx * 30), FONT)

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
