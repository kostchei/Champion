import sqlite3

# Connect to the database (it will be created if it doesn't exist)
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

# Create the "monsters" table
cursor.execute('''
CREATE TABLE IF NOT EXISTS monsters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    feature TEXT
)
''')

# Insert the example monster
cursor.execute('''
INSERT INTO monsters (CR, name, type, initiative, AC, hitpoints, loot, routine, a1_tohit, a1_damage, action1, a2_tohit, a2_damage, action2, resistance, feature)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    '1/2', 'worg', 'monstrosity', '+1', 13, '4d10+4', 'components', '{a1}', '+5', '2d6+3', 'attack', 'null', 'null', 'null', 'null', '{on hit: DC 13 strength save or prone}'
))

# Commit the transaction and close the connection
conn.commit()
conn.close()
