# utils/names.py

import random

def get_names():
    return ["Kim", "Ash", "Alex", "Bryn", "Blake", "Drew"]

def get_random_name():
    return random.choice(get_names())
