# utils/races.py
import json

def get_races():
    """
    Load the list of race names from the JSON file.

    Returns:
        list: A list of race names.
    """
    with open('./utils/races.json', 'r') as file:
        data = json.load(file)
    return list(data['races'].keys())

def get_race_details(race_name):
    """
    Get the details of a specific race from the JSON file.

    Args:
        race_name (str): The name of the race to get details for.

    Returns:
        dict: A dictionary containing the details of the race.
    """
    with open('./utils/races.json', 'r') as file:
        data = json.load(file)
    return data['races'].get(race_name, {})

