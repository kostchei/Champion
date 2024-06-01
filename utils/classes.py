# ./utils/classes.py
import json
import os

def get_classes():
    """
    Load the list of class names from the JSON files in the './classes/' directory.

    Returns:
        list: A list of class names.
    """
    class_files = [f for f in os.listdir('./classes') if f.endswith('.json')]
    classes = [os.path.splitext(f)[0] for f in class_files]
    return classes

def get_class_details(class_name):
    """
    Get the details of a specific class from the corresponding JSON file.

    Args:
        class_name (str): The name of the class to get details for.

    Returns:
        dict: A dictionary containing the details of the class.
    """
    file_path = f'./classes/{class_name}.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    else:
        return {}

# Example usage
if __name__ == "__main__":
    classes = get_classes()
    print("Available classes:", classes)

    class_name = 'Fighter'
    details = get_class_details(class_name)
    print(f"Details for {class_name}:", details)


