import json
import sqlite3

# Define the path to your JSON file and the database file
json_file_path = 'magicvariants.json'
db_file_path = 'game_database.db'

# Read and parse the JSON file
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Connect to the SQLite database
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Extract column names from the UniversalEquipment table
cursor.execute("PRAGMA table_info(UniversalEquipment);")
columns_info = cursor.fetchall()
columns = [info[1] for info in columns_info]

# Helper function to convert JSON item to a dictionary matching table schema
def convert_item_to_db_entry(item):
    item_details = {
        'Name': item['name'],
        'Item_Type': item.get('type', ''),
        'Description': ' '.join([str(entry) for entry in item.get('entries', [])])
    }
    
    # Flatten inherited attributes
    if 'inherits' in item:
        inherited = item['inherits']
        item_details.update({
            'Description': item_details['Description'] + ' ' + ' '.join([str(entry) for entry in inherited.get('entries', [])]),
            'Bonus_Weapon': inherited.get('bonusWeapon', ''),
            'Loot_Tables': ', '.join(inherited.get('lootTables', [])),
            'Tier': inherited.get('tier', ''),
            'Rarity': inherited.get('rarity', ''),
            'Source': inherited.get('source', ''),
            'Page': inherited.get('page', ''),
            'SRD': inherited.get('srd', False)
        })
    
    # Handle additional fields from the original item
    if 'requires' in item:
        item_details['Requires'] = json.dumps(item['requires'])
    
    if 'ammo' in item:
        item_details['Ammo'] = item['ammo']
    
    return item_details

# Filter and prepare items to insert or update
items_to_insert_or_update = []
for item in data['magicvariant']:
    if item.get('inherits', {}).get('source') == 'DMG':
        item_details = convert_item_to_db_entry(item)
        items_to_insert_or_update.append(item_details)

# Insert or update items in the UniversalEquipment table
for item in items_to_insert_or_update:
    columns_str = ', '.join([col for col in item.keys() if col in columns])
    placeholders = ', '.join(['?' for _ in item if _ in columns])
    sql = f"INSERT OR REPLACE INTO UniversalEquipment ({columns_str}) VALUES ({placeholders})"
    try:
        cursor.execute(sql, [item[col] for col in item.keys() if col in columns])
    except sqlite3.OperationalError as e:
        print(f"Error inserting or updating item {item['Name']}: {e}")

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Items from magicvariants.json with source 'DMG' have been uploaded to UniversalEquipment table.")
