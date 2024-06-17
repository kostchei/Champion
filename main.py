import os
import subprocess
import sys
import pygame as pg

# Initialize Pygame
pg.init()
pg.font.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 920
BUTTON_WIDTH, BUTTON_HEIGHT = 250, 60
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

# Set up the screen
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Main Menu")

script_dir = os.path.dirname(os.path.abspath(__file__))
maps_dir = os.path.join(script_dir, "maps")

def run_script(script_name, *args):
    script_path = os.path.join(script_dir, script_name)
    subprocess.run([sys.executable, script_path, *args])

def draw_button(text, position):
    mouse_pos = pg.mouse.get_pos()
    button_rect = pg.Rect(*position, BUTTON_WIDTH, BUTTON_HEIGHT)
    shadow_rect = pg.Rect(position[0] + 5, position[1] + 5, BUTTON_WIDTH, BUTTON_HEIGHT)
    color = COLORS["button_hover"] if button_rect.collidepoint(mouse_pos) else COLORS["button"]

    pg.draw.rect(screen, COLORS["button_shadow"], shadow_rect, border_radius=10)
    pg.draw.rect(screen, color, button_rect, border_radius=10)
    pg.draw.rect(screen, COLORS["popup_border"], button_rect, 2, border_radius=10)

    text_surface = FONT.render(text, True, COLORS["button_text"])
    screen.blit(text_surface, text_surface.get_rect(center=button_rect.center))
    return button_rect

def draw_popup(text, position, width, height):
    popup_rect = pg.Rect(*position, width, height)
    pg.draw.rect(screen, COLORS["popup"], popup_rect, border_radius=10)
    pg.draw.rect(screen, COLORS["popup_border"], popup_rect, 2, border_radius=10)

    text_surface = POPUP_FONT.render(text, True, COLORS["popup_border"])
    screen.blit(text_surface, text_surface.get_rect(center=(position[0] + width // 2, position[1] + height // 2)))
    return popup_rect

def choose_character():
    save_dir = os.path.join(script_dir, "saves")
    save_files = [f for f in os.listdir(save_dir) if f.endswith(".json") and len(f.split('.')) == 3]
    if not save_files:
        print("No characters found. Returning to main menu.")
        return

    while True:
        screen.fill(COLORS["background"])
        popup_rect = draw_popup("Choose a character to load:", (200, 200), 400, 50)
        button_positions = [(275, 270 + i * (BUTTON_HEIGHT + BUTTON_PADDING)) for i in range(len(save_files))]

        for i, pos in enumerate(button_positions):
            rect = draw_button(f"{i + 1}. {save_files[i]}", pos)
            if pg.mouse.get_pressed()[0] and rect.collidepoint(pg.mouse.get_pos()):
                run_script("csdisplay.py", os.path.join(save_dir, save_files[i]))
                return

        if any(event.type == pg.QUIT for event in pg.event.get()):
            pg.quit()
            return
        pg.display.flip()

def main_menu():
    buttons = [
        ("Create Character", "ccmenu.py"),
        ("New Map", "overland.py"),
        ("Continue Game", None),
        ("Generate Encounter", "DM_Enc_tool.py"),
        ("Backpack", "inventory.py"),
        ("Level Up", "leveling.py"),
        ("Camp", "camp.py"),
        ("Choose Character", choose_character),
        ("Exit", None)
    ]

    while True:
        screen.fill(COLORS["background"])
        for i, (text, script) in enumerate(buttons):
            rect = draw_button(text, (275, 100 + i * (BUTTON_HEIGHT + BUTTON_PADDING)))
            if pg.mouse.get_pressed()[0] and rect.collidepoint(pg.mouse.get_pos()):
                if text == "New Map":
                    run_script(script)
                    generated_files = [f for f in os.listdir(maps_dir) if f.startswith("hex_map_") and f.endswith(".json")]
                    if generated_files:
                        latest_map = max(generated_files, key=lambda f: os.path.getctime(os.path.join(maps_dir, f)))
                        print(f"Loading the latest generated map: {os.path.join(maps_dir, latest_map)}")
                        run_script("explorer.py", os.path.join(maps_dir, latest_map))
                    else:
                        print("No maps generated. Returning to main menu.")
                elif text == "Continue Game":
                    generated_files = [f for f in os.listdir(maps_dir) if f.startswith("hex_map_") and f.endswith(".json")]
                    if generated_files:
                        latest_map = max(generated_files, key=lambda f: os.path.getctime(os.path.join(maps_dir, f)))
                        print(f"Loading the most recent map: {os.path.join(maps_dir, latest_map)}")
                        run_script("explorer.py", os.path.join(maps_dir, latest_map))
                    else:
                        print("No maps found. Returning to main menu.")
                elif text == "Exit":
                    pg.quit()
                    return
                elif callable(script):
                    script()
                else:
                    run_script(script)

        if any(event.type == pg.QUIT for event in pg.event.get()):
            pg.quit()
            return
        pg.display.flip()

if __name__ == '__main__':
    main_menu()
