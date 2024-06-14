# main.py
import os
import subprocess
import sys
import pygame as pg
from datetime import datetime

# Initialize Pygame
pg.init()
pg.font.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 920
BUTTON_WIDTH, BUTTON_HEIGHT = 250, 60
BUTTON_PADDING = 20
BUTTON_COLOR = (240, 240, 230)  # GREY
BUTTON_HOVER_COLOR = (237, 243, 252)  # WHITE
BUTTON_TEXT_COLOR = (30, 40, 50)  # DARK_BLUE
BACKGROUND_COLOR = (247, 246, 237)  # BUFF_OFF_WHITE
BUTTON_SHADOW_COLOR = (200, 200, 180)  # Light brown shadow (not provided, derived for shadow)
FONT = pg.font.SysFont('Arial', 24)
POPUP_FONT = pg.font.SysFont('Arial', 20)

# Set up the screen with calculated size
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Main Menu")

script_dir = os.path.dirname(os.path.abspath(__file__))
maps_dir = os.path.join(script_dir, "maps")

def run_script(script_name, *args):
    script_path = os.path.join(script_dir, script_name)
    subprocess.run([sys.executable, script_path, *args])

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

def draw_popup(text, position, width, height):
    popup_rect = pg.Rect(position[0], position[1], width, height)
    pg.draw.rect(screen, (255, 255, 255), popup_rect, border_radius=10)  # White background
    pg.draw.rect(screen, (0, 0, 0), popup_rect, 2, border_radius=10)  # Border

    text_surface = POPUP_FONT.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(position[0] + width // 2, position[1] + height // 2))
    screen.blit(text_surface, text_rect)

    return popup_rect

def choose_character():
    save_dir = os.path.join(script_dir, "saves")
    save_files = [f for f in os.listdir(save_dir) if f.endswith(".json") and len(f.split('.')) == 3]
    if not save_files:
        print("No characters found. Returning to main menu.")
        return

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        screen_rect = screen.get_rect()
        popup_width, popup_height = 400, 300
        popup_rect = draw_popup("Choose a character to load:", (screen_rect.centerx - popup_width // 2, screen_rect.centery - popup_height // 2 - 50), popup_width, 50)
        button_positions = [(screen_rect.centerx - BUTTON_WIDTH // 2, popup_rect.bottom + BUTTON_PADDING + i * (BUTTON_HEIGHT + BUTTON_PADDING)) for i in range(len(save_files))]

        button_rects = []
        for i, pos in enumerate(button_positions):
            rect = draw_button(f"{i + 1}. {save_files[i]}", pos)
            button_rects.append((save_files[i], rect))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for file, rect in button_rects:
                    if rect.collidepoint(event.pos):
                        filename = os.path.join(save_dir, file)
                        run_script("csdisplay.py", filename)
                        return  # Exit after loading character

        pg.display.flip()

def main_menu():
    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)  # Background color

        # Draw buttons
        buttons = [
            ("Create Character", (SCREEN_WIDTH//2 - BUTTON_WIDTH//2, 100)),
            ("New Map", (SCREEN_WIDTH//2 - BUTTON_WIDTH//2, 100 + BUTTON_HEIGHT + BUTTON_PADDING)),
            ("Continue Game", (SCREEN_WIDTH//2 - BUTTON_WIDTH//2, 100 + 2*(BUTTON_HEIGHT + BUTTON_PADDING))),
            ("Generate Encounter", (SCREEN_WIDTH//2 - BUTTON_WIDTH//2, 100 + 3*(BUTTON_HEIGHT + BUTTON_PADDING))),
            ("Backpack", (SCREEN_WIDTH//2 - BUTTON_WIDTH//2, 100 + 4*(BUTTON_HEIGHT + BUTTON_PADDING))),
            ("Level Up", (SCREEN_WIDTH//2 - BUTTON_WIDTH//2, 100 + 5*(BUTTON_HEIGHT + BUTTON_PADDING))),
            ("Camp", (SCREEN_WIDTH//2 - BUTTON_WIDTH//2, 100 + 6*(BUTTON_HEIGHT + BUTTON_PADDING))),
            ("Choose Character", (SCREEN_WIDTH//2 - BUTTON_WIDTH//2, 100 + 7*(BUTTON_HEIGHT + BUTTON_PADDING))),
            ("Exit", (SCREEN_WIDTH//2 - BUTTON_WIDTH//2, 100 + 8*(BUTTON_HEIGHT + BUTTON_PADDING))),
        ]

        button_rects = []
        for text, pos in buttons:
            rect = draw_button(text, pos)
            button_rects.append((text, rect))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                for text, rect in button_rects:
                    if rect.collidepoint(event.pos):
                        if text == "Create Character":
                            run_script("ccmenu.py")
                        elif text == "New Map":
                            run_script("overland.py")
                            generated_files = [f for f in os.listdir(maps_dir) if f.startswith("hex_map_") and f.endswith(".json")]
                            if not generated_files:
                                print("No maps generated. Returning to main menu.")
                                continue
                            latest_map = max(generated_files, key=lambda f: os.path.getctime(os.path.join(maps_dir, f)))
                            filename = os.path.join(maps_dir, latest_map)
                            print(f"Loading the latest generated map: {filename}")
                            run_script("explorer.py", filename)
                        elif text == "Continue Game":
                            generated_files = [f for f in os.listdir(maps_dir) if f.startswith("hex_map_") and f.endswith(".json")]
                            if not generated_files:
                                print("No maps found. Returning to main menu.")
                                continue
                            latest_map = max(generated_files, key=lambda f: os.path.getctime(os.path.join(maps_dir, f)))
                            filename = os.path.join(maps_dir, latest_map)
                            print(f"Loading the most recent map: {filename}")
                            run_script("explorer.py", filename)
                        elif text == "Generate Encounter":
                            run_script("DM_Enc_tool.py")
                        elif text == "Backpack":
                            run_script("inventory.py")
                        elif text == "Level Up":
                            run_script("leveling.py")
                        elif text == "Camp":
                            run_script("camp.py")
                        elif text == "Choose Character":
                            choose_character()
                        elif text == "Exit":
                            running = False

        pg.display.flip()
    pg.quit()

if __name__ == '__main__':
    main_menu()
