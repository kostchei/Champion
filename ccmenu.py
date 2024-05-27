# ccmenu.py
import pygame as pg
from pygame.locals import QUIT, MOUSEBUTTONDOWN, KEYDOWN, K_BACKSPACE, K_RETURN
from utils.names import get_random_name
from utils.races import get_races, get_random_race
import random
import json
import os
import subprocess

pg.init()

# Screen dimensions
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Colors
BUFF_OFF_WHITE = (247, 246, 237)
DARK_BLUE = (30, 40, 50)
WHITE = (237, 243, 252)
GREY = (240, 240, 230)

# Fonts
label_font = pg.font.Font(None, 36)
button_font = pg.font.Font(None, 18)

# Dropdown and button dimensions
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 40
LABEL_SPACING = 50

# Create screen
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Character Creation")

# Load dice icon
dice_icon = pg.image.load('./images/dice.png')
dice_icon = pg.transform.scale(dice_icon, (30, 30))

# Menu items
genders = ["Male", "Female"]
races = get_races()
classes = ["Fighter", "Rogue"]
backgrounds = ["Outlander", "Ruined", "Soldier", "Folk Hero"]
game_editions = ["Champion", "Skullduggery"]

# Default values
selected_name = ""
selected_gender = None
selected_race = None
selected_class = None
selected_background = None
selected_edition = "Champion"

# Function to draw text
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Function to draw dropdown menus
def draw_dropdown(surface, options, x, y, selected=None, active=False):
    pg.draw.rect(surface, WHITE, (x, y, BUTTON_WIDTH, BUTTON_HEIGHT))
    draw_text(selected if selected else "Select", button_font, DARK_BLUE, surface, x + 10, y + 5)
    if active:
        for i, option in enumerate(options):
            pg.draw.rect(surface, GREY, (x, y + (i + 1) * BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT))
            draw_text(option, button_font, DARK_BLUE, surface, x + 10, y + (i + 1) * BUTTON_HEIGHT + 5)

# Function to draw randomize button
def draw_random_button(surface, x, y):
    surface.blit(dice_icon, (x, y))

# Function to randomize all selections
def randomize_all():
    global selected_name, selected_gender, selected_race, selected_class, selected_background, selected_edition
    selected_name = get_random_name()
    selected_gender = random.choice(genders)
    selected_race = get_random_race()
    selected_class = random.choice(classes)
    selected_background = random.choice(backgrounds)
    selected_edition = random.choice(game_editions)

# Main loop
running = True
dropdown_open = None
name_active = False
finalized = False

while running:
    screen.fill(BUFF_OFF_WHITE)
    
    # Draw labels
    labels = ["Name", "Gender", "Game Edition", "Race", "Class", "Background"]
    for i, label in enumerate(labels):
        draw_text(label, label_font, DARK_BLUE, screen, 50 + i * (BUTTON_WIDTH + LABEL_SPACING), 20)
    
    # Draw name input box
    name_rect = pg.Rect(50, 60, BUTTON_WIDTH, BUTTON_HEIGHT)
    pg.draw.rect(screen, WHITE, name_rect, 2 if name_active else 0)  # Add border if active
    draw_text(selected_name, button_font, DARK_BLUE, screen, 60, 65)
    draw_random_button(screen, 260, 60)
    
    # Draw dropdown menus and randomize buttons
    draw_dropdown(screen, genders, 50 + (BUTTON_WIDTH + LABEL_SPACING), 60, selected_gender, dropdown_open == 'gender')
    draw_dropdown(screen, game_editions, 50 + 2 * (BUTTON_WIDTH + LABEL_SPACING), 60, selected_edition, dropdown_open == 'edition')
    draw_dropdown(screen, races, 50 + 3 * (BUTTON_WIDTH + LABEL_SPACING), 60, selected_race, dropdown_open == 'race')
    draw_dropdown(screen, classes, 50 + 4 * (BUTTON_WIDTH + LABEL_SPACING), 60, selected_class, dropdown_open == 'class')
    draw_dropdown(screen, backgrounds, 50 + 5 * (BUTTON_WIDTH + LABEL_SPACING), 60, selected_background, dropdown_open == 'background')

    draw_random_button(screen, 510, 60)
    draw_random_button(screen, 760, 60)
    draw_random_button(screen, 1010, 60)
    draw_random_button(screen, 1260, 60)
    draw_random_button(screen, 1510, 60)
    
    # Draw finalize button
    finalize_button_rect = pg.Rect(SCREEN_WIDTH - 250, 20, 200, BUTTON_HEIGHT)
    pg.draw.rect(screen, WHITE, finalize_button_rect)
    draw_text("Finalize", button_font, DARK_BLUE, screen, SCREEN_WIDTH - 240, 25)
    
    # Event handling
    for event in pg.event.get():
        if event.type == QUIT:
            running = False
        if event.type == MOUSEBUTTONDOWN:
            x, y = event.pos
            dropdown_open = None  # Reset dropdown_open initially
            
            if name_rect.collidepoint(x, y):
                name_active = True
            else:
                name_active = False
                
            if 260 <= x <= 290 and 60 <= y <= 90:
                selected_name = get_random_name()
                
            if 50 + (BUTTON_WIDTH + LABEL_SPACING) <= x <= 50 + (BUTTON_WIDTH + LABEL_SPACING) + BUTTON_WIDTH:
                if 60 <= y <= 60 + BUTTON_HEIGHT:
                    dropdown_open = 'gender' if dropdown_open != 'gender' else None
                elif 60 < y <= 60 + (len(genders) + 1) * BUTTON_HEIGHT:
                    selected_gender = genders[(y - 60) // BUTTON_HEIGHT - 1]
            elif 510 <= x <= 540 and 60 <= y <= 90:
                selected_gender = random.choice(genders)
            elif 50 + 2 * (BUTTON_WIDTH + LABEL_SPACING) <= x <= 50 + 2 * (BUTTON_WIDTH + LABEL_SPACING) + BUTTON_WIDTH:
                if 60 <= y <= 60 + BUTTON_HEIGHT:
                    dropdown_open = 'edition' if dropdown_open != 'edition' else None
                elif 60 < y <= 60 + (len(game_editions) + 1) * BUTTON_HEIGHT:
                    selected_edition = game_editions[(y - 60) // BUTTON_HEIGHT - 1]
            elif 760 <= x <= 790 and 60 <= y <= 90:
                selected_edition = random.choice(game_editions)
            elif 50 + 3 * (BUTTON_WIDTH + LABEL_SPACING) <= x <= 50 + 3 * (BUTTON_WIDTH + LABEL_SPACING) + BUTTON_WIDTH:
                if 60 <= y <= 60 + BUTTON_HEIGHT:
                    dropdown_open = 'race' if dropdown_open != 'race' else None
                elif 60 < y <= 60 + (len(races) + 1) * BUTTON_HEIGHT:
                    selected_race = races[(y - 60) // BUTTON_HEIGHT - 1]
            elif 1010 <= x <= 1040 and 60 <= y <= 90:
                selected_race = get_random_race()
            elif 50 + 4 * (BUTTON_WIDTH + LABEL_SPACING) <= x <= 50 + 4 * (BUTTON_WIDTH + LABEL_SPACING) + BUTTON_WIDTH:
                if 60 <= y <= 60 + BUTTON_HEIGHT:
                    dropdown_open = 'class' if dropdown_open != 'class' else None
                elif 60 < y <= 60 + (len(classes) + 1) * BUTTON_HEIGHT:
                    selected_class = classes[(y - 60) // BUTTON_HEIGHT - 1]
            elif 1260 <= x <= 1290 and 60 <= y <= 90:
                selected_class = random.choice(classes)
            elif 50 + 5 * (BUTTON_WIDTH + LABEL_SPACING) <= x <= 50 + 5 * (BUTTON_WIDTH + LABEL_SPACING) + BUTTON_WIDTH:
                if 60 <= y <= 60 + BUTTON_HEIGHT:
                    dropdown_open = 'background' if dropdown_open != 'background' else None
                elif 60 < y <= 60 + (len(backgrounds) + 1) * BUTTON_HEIGHT:
                    selected_background = backgrounds[(y - 60) // BUTTON_HEIGHT - 1]
            elif 1510 <= x <= 1540 and 60 <= y <= 90:
                selected_background = random.choice(backgrounds)
            elif finalize_button_rect.collidepoint(x, y):
                if not finalized:
                    finalized = True
                    if not selected_name:
                        selected_name = get_random_name()
                    print("Finalize button clicked!")
                    
                    # Prepare character data
                    character_data = {
                        "name": selected_name,
                        "gender": selected_gender,
                        "game_edition": selected_edition,
                        "race": selected_race,
                        "class": selected_class,
                        "background": selected_background
                    }

                    # Save character data to JSON
                    if not os.path.exists('./saves'):
                        os.makedirs('./saves')
                    with open('./saves/character.json', 'w') as f:
                        json.dump(character_data, f)

                    # Call the creator.py script
                    subprocess.run(['python', 'creator.py', './saves/character.json'])
                    
                    running = False  # Exit the current script after handing off to creator.py
            else:
                dropdown_open = None  # Close any dropdown if clicked outside

        if event.type == KEYDOWN:
            if name_active:  # Check if name box is active
                if event.key == K_RETURN:  # Handle Enter key press
                    name_active = False
                elif event.key == K_BACKSPACE:
                    selected_name = selected_name[:-1]  # Remove last character
                else:
                    selected_name += event.unicode  # Add typed character

    pg.display.flip()

pg.quit()
