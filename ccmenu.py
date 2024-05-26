# ccmenu.py

import pygame as pg
from pygame.locals import QUIT, MOUSEBUTTONDOWN
from utils.names import get_names, get_random_name
from utils.races import get_races, get_random_race
import random

pg.init()

# Screen dimensions
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Colors
BUFF_OFF_WHITE = (247, 246, 237)
DARK_BLUE = (34, 43, 56)
WHITE = (237, 243, 252)
GREY = (100, 100, 100)

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
names = get_names()
genders = ["Male", "Female"]
races = get_races()
classes = ["Fighter", "Rogue"]
backgrounds = ["Outlander", "Ruined", "Soldier", "Folk Hero"]
game_editions = ["Champion", "Skullduggery"]

# Default values
selected_name = None
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
while running:
    screen.fill(BUFF_OFF_WHITE)
    
    # Draw labels
    labels = ["Name", "Gender", "Game Edition", "Race", "Class", "Background"]
    for i, label in enumerate(labels):
        draw_text(label, label_font, DARK_BLUE, screen, 50 + i * (BUTTON_WIDTH + LABEL_SPACING), 20)
    
    # Draw dropdown menus and randomize buttons
    draw_dropdown(screen, names, 50, 60, selected_name, dropdown_open == 'name')
    draw_dropdown(screen, genders, 50 + (BUTTON_WIDTH + LABEL_SPACING), 60, selected_gender, dropdown_open == 'gender')
    draw_dropdown(screen, game_editions, 50 + 2 * (BUTTON_WIDTH + LABEL_SPACING), 60, selected_edition, dropdown_open == 'edition')
    draw_dropdown(screen, races, 50 + 3 * (BUTTON_WIDTH + LABEL_SPACING), 60, selected_race, dropdown_open == 'race')
    draw_dropdown(screen, classes, 50 + 4 * (BUTTON_WIDTH + LABEL_SPACING), 60, selected_class, dropdown_open == 'class')
    draw_dropdown(screen, backgrounds, 50 + 5 * (BUTTON_WIDTH + LABEL_SPACING), 60, selected_background, dropdown_open == 'background')

    draw_random_button(screen, 250, 60)
    draw_random_button(screen, 500, 60)
    draw_random_button(screen, 750, 60)
    draw_random_button(screen, 1000, 60)
    draw_random_button(screen, 1250, 60)
    draw_random_button(screen, 1500, 60)
    
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
            
            if 50 <= x <= 50 + BUTTON_WIDTH:
                if 60 <= y <= 60 + BUTTON_HEIGHT:
                    dropdown_open = 'name' if dropdown_open != 'name' else None
                elif 60 < y <= 60 + (len(names) + 1) * BUTTON_HEIGHT:
                    selected_name = names[(y - 60) // BUTTON_HEIGHT - 1]
            elif 250 <= x <= 280 and 60 <= y <= 90:
                selected_name = get_random_name()
            elif 50 + (BUTTON_WIDTH + LABEL_SPACING) <= x <= 50 + (BUTTON_WIDTH + LABEL_SPACING) + BUTTON_WIDTH:
                if 60 <= y <= 60 + BUTTON_HEIGHT:
                    dropdown_open = 'gender' if dropdown_open != 'gender' else None
                elif 60 < y <= 60 + (len(genders) + 1) * BUTTON_HEIGHT:
                    selected_gender = genders[(y - 60) // BUTTON_HEIGHT - 1]
            elif 500 <= x <= 530 and 60 <= y <= 90:
                selected_gender = random.choice(genders)
            elif 50 + 2 * (BUTTON_WIDTH + LABEL_SPACING) <= x <= 50 + 2 * (BUTTON_WIDTH + LABEL_SPACING) + BUTTON_WIDTH:
                if 60 <= y <= 60 + BUTTON_HEIGHT:
                    dropdown_open = 'edition' if dropdown_open != 'edition' else None
                elif 60 < y <= 60 + (len(game_editions) + 1) * BUTTON_HEIGHT:
                    selected_edition = game_editions[(y - 60) // BUTTON_HEIGHT - 1]
            elif 750 <= x <= 780 and 60 <= y <= 90:
                selected_edition = random.choice(game_editions)
            elif 50 + 3 * (BUTTON_WIDTH + LABEL_SPACING) <= x <= 50 + 3 * (BUTTON_WIDTH + LABEL_SPACING) + BUTTON_WIDTH:
                if 60 <= y <= 60 + BUTTON_HEIGHT:
                    dropdown_open = 'race' if dropdown_open != 'race' else None
                elif 60 < y <= 60 + (len(races) + 1) * BUTTON_HEIGHT:
                    selected_race = races[(y - 60) // BUTTON_HEIGHT - 1]
            elif 1000 <= x <= 1030 and 60 <= y <= 90:
                selected_race = get_random_race()
            elif 50 + 4 * (BUTTON_WIDTH + LABEL_SPACING) <= x <= 50 + 4 * (BUTTON_WIDTH + LABEL_SPACING) + BUTTON_WIDTH:
                if 60 <= y <= 60 + BUTTON_HEIGHT:
                    dropdown_open = 'class' if dropdown_open != 'class' else None
                elif 60 < y <= 60 + (len(classes) + 1) * BUTTON_HEIGHT:
                    selected_class = classes[(y - 60) // BUTTON_HEIGHT - 1]
            elif 1250 <= x <= 1280 and 60 <= y <= 90:
                selected_class = random.choice(classes)
            elif 50 + 5 * (BUTTON_WIDTH + LABEL_SPACING) <= x <= 50 + 5 * (BUTTON_WIDTH + LABEL_SPACING) + BUTTON_WIDTH:
                if 60 <= y <= 60 + BUTTON_HEIGHT:
                    dropdown_open = 'background' if dropdown_open != 'background' else None
                elif 60 < y <= 60 + (len(backgrounds) + 1) * BUTTON_HEIGHT:
                    selected_background = backgrounds[(y - 60) // BUTTON_HEIGHT - 1]
            elif 1500 <= x <= 1530 and 60 <= y <= 90:
                selected_background = random.choice(backgrounds)
            elif finalize_button_rect.collidepoint(x, y):
                print("Finalize button clicked!")
                # Here you can add the logic to finalize the character creation.
            else:
                dropdown_open = None  # Close any dropdown if clicked outside

    pg.display.flip()

pg.quit()