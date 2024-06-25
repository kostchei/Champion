import json
import sqlite3

def flatten_entries(entries):
    flattened = []
    for entry in entries:
        if isinstance(entry, str):
            flattened.append(entry)
        elif isinstance(entry, dict):
            # Handle dictionary entries
            if 'entries' in entry:
                flattened.extend(flatten_entries(entry['entries']))
            else:
                flattened.append(json.dumps(entry))  # Convert dict to JSON string
        elif isinstance(entry, list):
            flattened.extend(flatten_entries(entry))
        else:
            flattened.append(str(entry))
    return flattened

def parse_and_insert_equipment(conn, item):
    cursor = conn.cursor()
    
    # Map JSON fields to database columns
    data = {
        'Name': item.get('name'),
        'Item_Type': item.get('type'),
        'Base_Weight': item.get('weight'),
        'Base_Value': item.get('value'),
        'Damage': item.get('dmg1'),
        'Range': item.get('range'),
        'Property': json.dumps(item.get('property')) if item.get('property') else None,
        'Dmg_Type': item.get('dmgType'),
        'Weapon': 1 if item.get('weapon') else 0,
        'Weapon_Category': item.get('weaponCategory'),
        'Bonus_Spell_Attack': item.get('bonusSpellAttack'),
        'Bonus_Spell_Save_DC': item.get('bonusSpellSaveDc'),
        'Req_Attune': item.get('reqAttune'),
        'Req_Attune_Tags': json.dumps(item.get('reqAttuneTags')) if item.get('reqAttuneTags') else None,
        'Focus': json.dumps(item.get('focus')) if item.get('focus') else None,
        'Wondrous': 1 if item.get('wondrous') else 0,
        'Bonus_Weapon': item.get('bonusWeapon'),
        'Tier': item.get('rarity')
    }
    
    # Construct the Description from 'entries' if it exists
    if 'entries' in item:
        flattened_entries = flatten_entries(item['entries'])
        data['Description'] = '\n'.join(flattened_entries)
    
    # Ensure all values are present, use None for missing values
    for key in data:
        if data[key] == '':
            data[key] = None
    
    # Construct the SQL query
    columns = ', '.join(data.keys())
    placeholders = ', '.join('?' * len(data))
    sql = f"INSERT OR REPLACE INTO UniversalEquipment ({columns}) VALUES ({placeholders})"
    
    # Execute the query
    try:
        cursor.execute(sql, list(data.values()))
        return True
    except sqlite3.Error as e:
        print(f"Error inserting item {item.get('name', 'Unknown')}:")
        print(f"SQLite error: {e}")
        print(f"SQL: {sql}")
        print("Data:")
        for key, value in data.items():
            print(f"  {key}: {value}")
        return False

# Connect to the database
conn = sqlite3.connect('game_database.db')

# Load JSON data from file
try:
    with open('items.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        equipment_data = json_data.get('item', [])
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    exit(1)
except FileNotFoundError:
    print("items.json file not found")
    exit(1)

print(f"Loaded {len(equipment_data)} items from items.json")

# Insert each item into the database
successful_inserts = 0
failed_inserts = 0
total_items = len(equipment_data)

for index, item in enumerate(equipment_data, 1):
    if parse_and_insert_equipment(conn, item):
        successful_inserts += 1
    else:
        failed_inserts += 1
    
    # Print progress every 100 items
    if index % 100 == 0:
        print(f"Processed {index}/{total_items} items...")

# Commit changes and close the connection
conn.commit()
conn.close()

print(f"Data insertion complete.")
print(f"Successfully inserted: {successful_inserts}")
print(f"Failed to insert: {failed_inserts}")
print(f"Total items processed: {total_items}")