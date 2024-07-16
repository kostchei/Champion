import sqlite3
import json

# Function to create the monsters table if it doesn't exist
def create_monsters_table(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monsters (
            id INTEGER PRIMARY KEY,
            CR TEXT,
            name TEXT,
            type TEXT,
            initiative TEXT,
            AC INTEGER,
            hitpoints TEXT,
            loot TEXT,
            routine TEXT,
            a1_tohit TEXT,
            a1_damage TEXT,
            action1 TEXT,
            a2_tohit TEXT,
            a2_damage TEXT,
            action2 TEXT,
            resistance TEXT,
            feature TEXT,
            realm TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Function to insert a monster into the monsters table
def insert_monster(db_path, monster_data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO monsters (CR, name, type, initiative, AC, hitpoints, loot, routine, a1_tohit, a1_damage, action1, a2_tohit, a2_damage, action2, resistance, feature, realm)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', monster_data)
    
    conn.commit()
    conn.close()

# Function to load JSON data and insert it into the database
def load_json_to_db(json_path, db_path, realm):
    with open(json_path, 'r') as file:
        data = json.load(file)
        monsters = data['monster']
        
        for monster in monsters:
            # Add realm to monster data
            monster_data = (
                monster.get('CR'),
                monster.get('name'),
                monster.get('type'),
                monster.get('initiative'),
                monster.get('AC'),
                monster.get('hitpoints'),
                monster.get('loot'),
                monster.get('routine'),
                monster.get('a1_tohit'),
                monster.get('a1_damage'),
                monster.get('action1'),
                monster.get('a2_tohit'),
                monster.get('a2_damage'),
                monster.get('action2'),
                monster.get('resistance'),
                monster.get('feature'),
                realm
            )
            insert_monster(db_path, monster_data)

# Main function to execute the script
def main():
    json_path = 'griffwood2.json'
    db_path = 'game_database.db'
    realm = 'griffonwood'
    
    create_monsters_table(db_path)
    load_json_to_db(json_path, db_path, realm)

if __name__ == '__main__':
    main()
