import json
import sys
import pygame as pg

# Initialize Pygame
pg.init()
pg.font.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FONT = pg.font.SysFont('Arial', 24)

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

def combat_loop(player_data, encounter_data):
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Combat GUI")

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.fill((255, 255, 255))  # White background
        draw_text(screen, f"Player: {player_data['name']}", (20, 20), FONT)
        draw_text(screen, f"HP: {player_data['hit_points']}", (20, 50), FONT)

        # Display encounter details
        draw_text(screen, f"Difficulty: {encounter_data['difficulty']}", (20, 80), FONT)
        draw_text(screen, f"XP Budget: {encounter_data['xp_budget']}", (20, 110), FONT)

        # Access and display monster data from encounter_data
        monsters_data = encounter_data['encounter']
        for idx, monster in enumerate(monsters_data):
            y_offset = 140 + idx * 400
            draw_text(screen, f"Monster {idx + 1}: {monster['name']}", (20, y_offset), FONT)
            draw_text(screen, f"Size: {monster.get('size', 'N/A')}", (20, y_offset + 30), FONT)
            draw_text(screen, f"Type: {monster.get('type', 'N/A')}", (20, y_offset + 60), FONT)
            draw_text(screen, f"Alignment: {', '.join(monster.get('alignment', ['N/A']))}", (20, y_offset + 90), FONT)
            draw_text(screen, f"HP: {monster.get('hp', {}).get('average', 'N/A')} ({monster.get('hp', {}).get('formula', 'N/A')})", (20, y_offset + 120), FONT)
            draw_text(screen, f"AC: {monster.get('ac', 'N/A')}", (20, y_offset + 150), FONT)
            draw_text(screen, f"Speed: {monster.get('speed', {}).get('walk', 'N/A')} ft.", (20, y_offset + 180), FONT)
            draw_text(screen, f"CR: {monster.get('cr', 'N/A')}", (20, y_offset + 210), FONT)
            draw_text(screen, f"STR: {monster.get('str', 'N/A')}", (20, y_offset + 240), FONT)
            draw_text(screen, f"DEX: {monster.get('dex', 'N/A')}", (20, y_offset + 270), FONT)
            draw_text(screen, f"CON: {monster.get('con', 'N/A')}", (20, y_offset + 300), FONT)
            draw_text(screen, f"INT: {monster.get('int', 'N/A')}", (20, y_offset + 330), FONT)
            draw_text(screen, f"WIS: {monster.get('wis', 'N/A')}", (20, y_offset + 360), FONT)
            draw_text(screen, f"CHA: {monster.get('cha', 'N/A')}", (20, y_offset + 390), FONT)
            draw_text(screen, f"Actions:", (20, y_offset + 420), FONT)

            actions = monster.get('action', [])
            for action_idx, action in enumerate(actions):
                draw_text(screen, f"- {action}", (40, y_offset + 450 + action_idx * 30), FONT)

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
