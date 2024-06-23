import sqlite3
import json

def trim_json(json_string):
    try:
        # Parse the JSON string
        data = json.loads(json_string)
        
        # Check if it's in the old format (list with one dict with "_" key)
        if isinstance(data, list) and len(data) == 1 and "_" in data[0]:
            # Extract and return the inner list
            return json.dumps(data[0]["_"])
        else:
            # If it's already in the new format, return as is
            return json_string
    except json.JSONDecodeError:
        print(f"Error decoding JSON: {json_string}")
        return json_string

# Connect to the SQLite database
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

# Fetch all rows from the backgrounds table
cursor.execute("SELECT rowid, startingEquipment FROM backgrounds")
rows = cursor.fetchall()

# Process each row
for row in rows:
    rowid, starting_equipment = row
    
    # Trim the JSON
    trimmed_json = trim_json(starting_equipment)
    
    # Update the row with the trimmed JSON
    cursor.execute("UPDATE backgrounds SET startingEquipment = ? WHERE rowid = ?", (trimmed_json, rowid))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database update completed.")