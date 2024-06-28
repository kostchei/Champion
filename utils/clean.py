import sqlite3
import json  # For handling JSON data in the column

# Database Setup
db_path = 'game_database.db'  # Update if your database file is elsewhere
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fetch Data
cursor.execute("SELECT skill_proficiencies FROM classes")
rows = cursor.fetchall()

# Extract Skill Proficiencies
skill_list = []
for row in rows:
    skill_data = json.loads(row[0])  # Assuming data is stored as JSON
    if isinstance(skill_data, list):
        skill_list.extend(skill_data)
    # Handle cases where skill_data might be a dictionary, if needed
    # Example: if isinstance(skill_data, dict) and 'choose' in skill_data: ... 

# Print or Save to File
print(skill_list)  # Print to console

# Optional: Save to File
output_file = 'skill_proficiencies.txt'
with open(output_file, 'w') as f:
    for skill in skill_list:
        f.write(skill + '\n')

conn.close() 