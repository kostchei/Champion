import tkinter as tk

def create_character_frame(parent, character):
    """ Create the character frame. """
    frame = tk.Frame(parent, bg="#F7F6ED")
    tk.Label(frame, text="Character Details", font=("Arial", 16), bg="#F7F6ED").pack(pady=10)
    # Add more character details here
    return frame
