import tkinter as tk

def create_stats_frame(parent, character):
    """ Create the stats frame. """
    frame = tk.Frame(parent, bg="#F7F6ED")
    stats = ["Strength", "Intelligence", "Wisdom", "Dexterity", "Constitution", "Charisma"]
    for stat in stats:
        tk.Label(frame, text=f"{stat}: {character[stat.lower()]}", font=("Arial", 12), bg="#F7F6ED").pack(pady=5)
    return frame
