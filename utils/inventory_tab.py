import tkinter as tk

def create_inventory_frame(parent):
    """ Create the inventory frame. """
    frame = tk.Frame(parent, bg="#F7F6ED")
    tk.Label(frame, text="Inventory Details", font=("Arial", 16), bg="#F7F6ED").pack(pady=10)
    # Add inventory details here
    return frame
