import tkinter as tk
from tkinter import ttk
import json
import os
import subprocess
import random
from PIL import Image, ImageTk
from utils.names import get_random_name
from utils.game_editions import get_active_game_editions
from utils.races import get_races, get_race_details, get_races_for_editions
from utils.classes import get_classes, get_class_details
from utils.backgrounds import get_backgrounds, get_background_details

root = tk.Tk()
root.title("Character Generator")
root.configure(bg="#F7F6ED")
root.geometry("1920x1080")

genders = ["Male", "Female"]
game_editions = get_active_game_editions()
backgrounds = get_backgrounds()
edition_name_to_id = {name: id for name, id in game_editions.items()}

selected_name = tk.StringVar()
selected_gender = tk.StringVar(value="Male")
selected_race = tk.StringVar(value="Human")
selected_class = tk.StringVar(value="Fighter")
selected_background = tk.StringVar(value="Outlander")
show_campaign_specific = tk.BooleanVar(value=False)

dice_image = Image.open("./images/dice.png")
dice_image = dice_image.resize((40, 40), Image.Resampling.LANCZOS)
dice_icon = ImageTk.PhotoImage(dice_image)

def create_labeled_input(frame, label_text, options, selected_var, randomize_command):
    tk.Label(frame, text=label_text, bg="#F7F6ED", fg="darkblue", font=("Arial", 20)).pack(side=tk.LEFT)
    create_dropdown(frame, options, selected_var)
    create_random_button(frame, randomize_command)

def create_dropdown(parent, options, selected_var):
    dropdown = ttk.Combobox(parent, values=options, textvariable=selected_var, font=("Arial", 20))
    dropdown.pack(side=tk.LEFT, padx=5)
    dropdown.option_add('*TCombobox*Listbox.font', ("Arial", 20))
    return dropdown

def create_random_button(parent, command):
    tk.Button(parent, image=dice_icon, command=command, bg="#F7F6ED", bd=0).pack(side=tk.LEFT, padx=5)

def randomize_name():
    selected_name.set(get_random_name())

def randomize_gender():
    selected_gender.set(random.choice(genders))

def randomize_race():
    if races:
        selected_race.set(random.choice(races))

def randomize_class():
    if classes:
        selected_class.set(random.choice(classes))

def randomize_background():
    selected_background.set(random.choice(backgrounds))

def update_classes():
    active_editions = [edition for edition, var in selected_editions.items() if var.get()]
    global classes
    classes = get_classes(active_editions)
    class_dropdown['values'] = classes
    selected_class.set(classes[0] if classes else "")

def update_races():
    active_editions = [edition_name_to_id[edition] for edition, var in selected_editions.items() if var.get()]
    global races
    races = get_races_for_editions(active_editions)
    race_dropdown['values'] = races
    selected_race.set(races[0] if races else "")

def update_backgrounds():
    global backgrounds
    backgrounds = get_backgrounds()
    if not show_campaign_specific.get():
        backgrounds = [bg for bg in backgrounds if not get_background_details(bg).get('campaign_specific', 0)]
    background_dropdown['values'] = backgrounds
    selected_background.set(backgrounds[0] if backgrounds else "")

def create_checkbox_list(frame, label_text, options, selected_vars):
    tk.Label(frame, text=label_text, bg="#F7F6ED", fg="darkblue", font=("Arial", 20)).pack(anchor=tk.W)
    for option in options:
        var = tk.BooleanVar(value=(option == "Champion"))
        tk.Checkbutton(frame, text=option, variable=var, bg="#F7F6ED", font=("Arial", 20),
                       command=lambda: [update_classes(), update_races(), update_backgrounds()]).pack(anchor=tk.W)
        selected_vars[option] = var

def finalise_character():
    character_data = {
        "name": selected_name.get() or get_random_name(),
        "gender": selected_gender.get(),
        "game_editions": [edition for edition, var in selected_editions.items() if var.get()],
        "race": selected_race.get(),
        "class": selected_class.get(),
        "background": selected_background.get()
    }
    
    class_details = get_class_details(character_data["class"])
    character_data.update(class_details)
    
    race_details = get_race_details(character_data["race"])
    character_data.update(race_details)

    background_details = get_background_details(character_data["background"])
    character_data.update({
        "skillProficiencies": background_details.get("skillProficiencies"),
        "languageProficiencies": background_details.get("languageProficiencies"),
        "startingEquipment": background_details.get("startingEquipment"),
        "entries": background_details.get("entries")
    })

    if not os.path.exists('./saves'):
        os.makedirs('./saves')
    with open('./saves/character.json', 'w') as f:
        json.dump(character_data, f)

    subprocess.run(['python', 'creator.py', './saves/character.json'])

content_frame = tk.Frame(root, bg="#F7F6ED")
content_frame.place(relx=0.1, rely=0.1, relwidth=0.6, relheight=0.8)

frame = tk.Frame(content_frame, bg="#F7F6ED")
frame.pack(pady=10)
tk.Label(frame, text="Name:", bg="#F7F6ED", fg="darkblue", font=("Arial", 20)).pack(side=tk.LEFT)
tk.Entry(frame, textvariable=selected_name, font=("Arial", 20)).pack(side=tk.LEFT, padx=5)
create_random_button(frame, randomize_name)

frame1 = tk.Frame(content_frame, bg="#F7F6ED")
frame1.pack(pady=10)
create_labeled_input(frame1, "Gender:", genders, selected_gender, randomize_gender)

frame_bg = tk.Frame(content_frame, bg="#F7F6ED")
frame_bg.pack(pady=10, fill='x')
tk.Label(frame_bg, text="Background:", bg="#F7F6ED", fg="darkblue", font=("Arial", 20)).pack(side=tk.LEFT)
background_dropdown = create_dropdown(frame_bg, backgrounds, selected_background)
create_random_button(frame_bg, randomize_background)
tk.Checkbutton(frame_bg, text="Show Campaign Specific", variable=show_campaign_specific, bg="#F7F6ED", font=("Arial", 20),
               command=update_backgrounds).pack(side=tk.LEFT, padx=5)

frame2 = tk.Frame(content_frame, bg="#F7F6ED")
frame2.pack(pady=10)
tk.Label(frame2, text="Lineage:", bg="#F7F6ED", fg="darkblue", font=("Arial", 20)).pack(side=tk.LEFT)
race_dropdown = create_dropdown(frame2, [], selected_race)
create_random_button(frame2, randomize_race)

frame3 = tk.Frame(content_frame, bg="#F7F6ED")
frame3.pack(pady=10)
tk.Label(frame3, text="Class:", bg="#F7F6ED", fg="darkblue", font=("Arial", 20)).pack(side=tk.LEFT)
class_dropdown = create_dropdown(frame3, [], selected_class)
create_random_button(frame3, randomize_class)

# Game Edition Selection and Finalize Button on the right
edition_frame = tk.Frame(root, bg="#F7F6ED")
edition_frame.place(relx=0.75, rely=0.1, relwidth=0.2, relheight=0.8)

selected_editions = {}
create_checkbox_list(edition_frame, "Game Edition:", game_editions.keys(), selected_editions)

finalise_button = tk.Button(edition_frame, text="Finalise", command=finalise_character, bg="#F7F6ED", fg="darkblue", font=("Arial", 20))
finalise_button.pack(pady=20)

update_backgrounds()
root.mainloop()
