import random

def roll_dice(number, sides):
    return sum(random.randint(1, sides) for _ in range(number))
