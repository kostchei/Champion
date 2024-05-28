import json

def get_backgrounds():

    with open('./utils/backgrounds.json', 'r') as file:
        data = json.load(file)
    return list(data['backgrounds'].keys())

def get_background_details(background_name):

    with open('./utils/backgrounds.json', 'r') as file:
        data = json.load(file)
    return data['backgrounds'].get(background_name, {})
