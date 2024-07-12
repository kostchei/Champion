import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

# Query to find active characters
cursor.execute('''
    SELECT * FROM characters WHERE active = 'true'
''')

# Fetch all results
active_characters = cursor.fetchall()

# Check if there are any active characters and print them
if active_characters:
    print("Active characters found:")
    for character in active_characters:
        print(character)
else:
    print("No active characters found.")

# Close the connection
conn.close()
