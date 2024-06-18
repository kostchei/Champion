import json
import os
import pygame as pg

# Initialize Pygame
pg.init()
pg.font.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
BOTTOM_BUTTON_SIZE = (200, 40)
BOTTOM_BUTTON_PADDING = 20
BUTTON_COLOR = (240, 240, 230)
BUTTON_HOVER_COLOR = (237, 243, 252)
BUTTON_TEXT_COLOR = (30, 40, 50)
BACKGROUND_COLOR = (247, 246, 237)
BUTTON_SHADOW_COLOR = (200, 200, 180)
FONT = pg.font.SysFont('Arial', 14)

# Set up the screen
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Combat GUI")

# Load JSON options
def load_menu_options(menu_name):
    file_path = os.path.join('menu_options', f'{menu_name}.json')
    print(f"Loading menu options from {file_path}")  # Debug statement
    try:
        with open(file_path, 'r') as f:
            return json.load(f).get('options', [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading menu options: {e}")
        return []

# Draw button
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

# Draw pull-up menu
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

# Invoke script
def invoke_script(option):
    script_path = f"./utils/{option.lower().replace(' ', '_')}.py"
    result = os.popen(f"python {script_path}").read()
    return result

# Combat loop
def combat_loop():
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
                            print(f"Selected option: {option}")  # Debug output
                            result = invoke_script(option)
                            print(f"Script result: {result}")  # Debug output
                            active_menu = None
                            break
                else:
                    buttons = ["1.Move", "2.Action", "3.Bonus", "4.Reaction", "5.Free Action", "6.Spellbook", "7.Complete"]
                    total_width = len(buttons) * (BOTTOM_BUTTON_SIZE[0] + BOTTOM_BUTTON_PADDING) - BOTTOM_BUTTON_PADDING
                    start_x = (SCREEN_WIDTH - total_width) // 2
                    for i, text in enumerate(buttons):
                        button_rect = draw_button(text, (start_x + i * (BOTTOM_BUTTON_SIZE[0] + BOTTOM_BUTTON_PADDING), SCREEN_HEIGHT - BOTTOM_BUTTON_SIZE[1] - 20), BOTTOM_BUTTON_SIZE)
                        if button_rect.collidepoint(event.pos):
                            active_button = i + 1
                            active_menu = load_menu_options(f'c{active_button}move')
                            menu_rects = draw_pull_up_menu(active_menu, (start_x + i * (BOTTOM_BUTTON_SIZE[0] + BOTTOM_BUTTON_PADDING), SCREEN_HEIGHT - BOTTOM_BUTTON_SIZE[1] - 20))
                            break
            elif event.type == pg.KEYDOWN:
                if event.key in [pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6, pg.K_7]:
                    key_to_button = {pg.K_1: 1, pg.K_2: 2, pg.K_3: 3, pg.K_4: 4, pg.K_5: 5, pg.K_6: 6, pg.K_7: 7}
                    active_button = key_to_button[event.key]
                    active_menu = load_menu_options(f'c{active_button}move')
                    start_x = (SCREEN_WIDTH - (len(key_to_button) * (BOTTOM_BUTTON_SIZE[0] + BOTTOM_BUTTON_PADDING) - BOTTOM_BUTTON_PADDING)) // 2
                    menu_rects = draw_pull_up_menu(active_menu, (start_x + (active_button - 1) * (BOTTOM_BUTTON_SIZE[0] + BOTTOM_BUTTON_PADDING), SCREEN_HEIGHT - BOTTOM_BUTTON_SIZE[1] - 20))

        screen.fill(BACKGROUND_COLOR)

        buttons = ["1.Move", "2.Action", "3.Bonus", "4.Reaction", "5.Free Action", "6.Spellbook", "7.Complete"]
        total_width = len(buttons) * (BOTTOM_BUTTON_SIZE[0] + BOTTOM_BUTTON_PADDING) - BOTTOM_BUTTON_PADDING
        start_x = (SCREEN_WIDTH - total_width) // 2
        for i, text in enumerate(buttons):
            draw_button(text, (start_x + i * (BOTTOM_BUTTON_SIZE[0] + BOTTOM_BUTTON_PADDING), SCREEN_HEIGHT - BOTTOM_BUTTON_SIZE[1] - 20), BOTTOM_BUTTON_SIZE)

        if active_menu:
            draw_pull_up_menu(active_menu, (start_x + (active_button - 1) * (BOTTOM_BUTTON_SIZE[0] + BOTTOM_BUTTON_PADDING), SCREEN_HEIGHT - BOTTOM_BUTTON_SIZE[1] - 20))

        pg.display.flip()

if __name__ == "__main__":
    combat_loop()
    pg.quit()
