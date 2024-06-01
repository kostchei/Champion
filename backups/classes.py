# ./utils/classes.py
import json

def get_classes():
    """
    Load the list of class names from the JSON file.

    Returns:
        list: A list of class names.
    """
    with open('./utils/classes.json', 'r') as file:
        data = json.load(file)
    return list(data['classes'].keys())

def get_class_details(class_name):
    """
    Get the details of a specific class from the JSON file.

    Args:
        class_name (str): The name of the class to get details for.

    Returns:
        dict: A dictionary containing the details of the class.
    """
    with open('./utils/classes.json', 'r') as file:
        data = json.load(file)
    return data['classes'].get(class_name, {})

