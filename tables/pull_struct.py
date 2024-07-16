import sqlite3

# Connect to the database
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

# Function to get table schema
def get_table_schema(table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    schema = cursor.fetchall()
    return schema

# Fetch the schema of the characters table
characters_schema = get_table_schema('characters')

# Print the schema
for column in characters_schema:
    print(column)

# Close the database connection
conn.close()
