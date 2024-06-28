import tkinter as tk

def create_log_frame(parent):
    """ Create the log frame. """
    frame = tk.Frame(parent, bg="#F7F6ED")
    tk.Label(frame, text="Log Details", font=("Arial", 16), bg="#F7F6ED").pack(pady=10)
    # Add log details here
    return frame
