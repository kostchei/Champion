import sqlite3
import json

# Load the data from the JSON file
json_file_path = 'experience_levels_extended.json'
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

# Connect to the SQLite database
db_file_path = 'game_database.db'
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Create the xp_lv_bonus table
create_table_query = '''
CREATE TABLE IF NOT EXISTS xp_lv_bonus (
    level INTEGER PRIMARY KEY,
    experience_points INTEGER,
    proficiency_bonus INTEGER
)
'''
cursor.execute(create_table_query)

# Insert data into the table
insert_query = '''
INSERT INTO xp_lv_bonus (level, experience_points, proficiency_bonus)
VALUES (?, ?, ?)
'''

for entry in data:
    level = entry['level']
    experience_points = entry['experience_points']
    proficiency_bonus = entry['proficiency_bonus']
    cursor.execute(insert_query, (level, experience_points, proficiency_bonus))

# Commit the transaction and close the connection
conn.commit()
conn.close()
