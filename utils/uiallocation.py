import tkinter as tk
from tkinterdnd2 import TkinterDnD
import json
import os

def on_drop(event, target_label):
    data = event.data
    target_label.config(text=data)

def create_draggable_label(root, text, x, y):
    label = tk.Label(root, text=text, relief="raised", padx=10, pady=5)
    label.place(x=x, y=y)
    label.dnd_bind('<<Drop>>', lambda e, lbl=label: on_drop(e, lbl))
    return label

def load_character_features(character_file):
    with open(character_file, 'r') as file:
        data = json.load(file)
    return data

def update_features(root, character_features):
    # Clear existing features if any
    for widget in root.pack_slaves():
        if isinstance(widget, tk.Label) and "Slot" not in widget.cget("text"):
            widget.destroy()
    x, y = 20, 100
    for feature, details in character_features.items():
        text = f"{feature}: {details['description']}"
        lbl = create_draggable_label(root, text, x, y)
        lbl.dnd_bind('<<DragInitCmd>>', lambda e, lbl=lbl: lbl.dnd_start(e, lbl))
        x += 220  # Increase x to place labels horizontally

def character_selected(value, root):
    character_file = f"./saves/{value}.json"
    features = load_character_features(character_file)
    update_features(root, features)

def main():
    root = TkinterDnD.Tk()
    root.title("Class Feature Allocation")

    # Character Selection
    character_list = os.listdir('./saves')
    character_names = [os.path.splitext(name)[0] for name in character_list]
    select_label = tk.Label(root, text="Select a character:")
    select_label.place(x=20, y=20)
    character_var = tk.StringVar(root)
    character_menu = tk.OptionMenu(root, character_var, *character_names, command=lambda value: character_selected(value, root))
    character_menu.place(x=150, y=20)

    # Drop targets - action slots
    x, y = 300, 50
    for i in range(1, 11):
        target = tk.Label(root, text=f"Slot {i}", relief="sunken", width=30, height=5)
        target.place(x=x, y=y)
        target.dnd_bind('<<Drop>>', lambda e, lbl=target: on_drop(e, lbl))
        x += 120  # Place targets horizontally

    root.geometry("1200x600")  # Set a larger size for the window
    root.mainloop()

if __name__ == "__main__":
    main()

