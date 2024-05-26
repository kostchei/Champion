# utils/races.py

import random

def get_races():
    return ["Oerdian", "Olve"]

def get_random_race():
    return random.choice(get_races())
