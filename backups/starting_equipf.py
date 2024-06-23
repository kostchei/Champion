import sqlite3
import json

def update_fighter_equipment():
    conn = sqlite3.connect('game_database.db')
    cursor = conn.cursor()

    # Define the new equipment options
    new_equipment = {
        "Heavy": ["Ring Mail", "Battleaxe", "Maul", "Hand Axe", "Shield", "Horned Helmet", "25 gold"],
        "Medium": ["Scale Mail", "Longsword", "Short Sword", "Shield", "Plumed Helmet", "5 gold"],
        "Light": ["Studded leather", "Rapier", "Short Sword", "Shield", "Fancy Hat with Feather"]
    }

    # Convert the equipment options to JSON
    new_equipment_json = json.dumps(new_equipment)

    # Update the starting_equipment column for the Fighter class
    cursor.execute('''
        UPDATE classes
        SET starting_equipment = ?
        WHERE name = 'Fighter'
    ''', (new_equipment_json,))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_fighter_equipment()
