import sqlite3

# Define the challenge rating list
challengeRatingList = [
    {"cr": "0", "xp": 10},
    {"cr": "1/8", "xp": 25},
    {"cr": "1/4", "xp": 50},
    {"cr": "1/2", "xp": 100},
    {"cr": 1, "xp": 200},
    {"cr": 2, "xp": 450},
    {"cr": 3, "xp": 700},
    {"cr": 4, "xp": 1100},
    {"cr": 5, "xp": 1800},
    {"cr": 6, "xp": 2300},
    {"cr": 7, "xp": 2900},
    {"cr": 8, "xp": 3900},
    {"cr": 9, "xp": 5000},
    {"cr": 10, "xp": 5900},
    {"cr": 11, "xp": 7200},
    {"cr": 12, "xp": 8400},
    {"cr": 13, "xp": 10000},
    {"cr": 14, "xp": 11500},
    {"cr": 15, "xp": 13000},
    {"cr": 16, "xp": 15000},
    {"cr": 17, "xp": 18000},
    {"cr": 18, "xp": 20000},
    {"cr": 19, "xp": 22000},
    {"cr": 20, "xp": 25000},
]

# Connect to the SQLite database
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

# Create the xp4cr table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS xp4cr (
        id INTEGER PRIMARY KEY,
        cr TEXT NOT NULL,
        xp INTEGER NOT NULL
    )
''')

# Insert the challenge rating data into the xp4cr table
for index, entry in enumerate(challengeRatingList, start=1):
    cursor.execute('''
        INSERT INTO xp4cr (id, cr, xp) VALUES (?, ?, ?)
    ''', (index, entry["cr"], entry["xp"]))

# Commit the changes and close the connection
conn.commit()
conn.close()
