import json
import os
import sys
import pygame as pg

# Initialize Pygame
pg.init()
pg.font.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FONT = pg.font.SysFont('Arial', 24)

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def draw_text(screen, text, position, font, color=(0, 0, 0)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def combat_loop(player_data, monsters_data):
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

        for idx, monster in enumerate(monsters_data):
            draw_text(screen, f"Monster {idx + 1}: {monster['name']}", (20, 100 + idx * 50), FONT)
            draw_text(screen, f"HP: {monster.get('hit_points', 'N/A')}", (20, 130 + idx * 50), FONT)

        pg.display.flip()

if __name__ == "__main__":
    encounter_file = sys.argv[1]
    encounter_data = load_json(encounter_file)

    player_data = {
        "name": encounter_data["player"],
        "hit_points": 100,  # Replace with actual player hit points if available
    }
    monsters_data = encounter_data["encounter"]

    combat_loop(player_data, monsters_data)
