import sqlite3

def reset_background_ids(db_connection):
    cursor = db_connection.cursor()

    # Get all remaining entries in order
    cursor.execute('SELECT * FROM backgrounds ORDER BY id')
    rows = cursor.fetchall()

    # Create a temporary table to hold the new sequence
    cursor.execute('''
        CREATE TEMPORARY TABLE temp_backgrounds (
            new_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            skillProficiencies TEXT,
            languageProficiencies TEXT,
            startingEquipment TEXT,
            entries TEXT,
            features TEXT
        )
    ''')

    # Insert data into the temporary table
    for row in rows:
        cursor.execute('''
            INSERT INTO temp_backgrounds (name, skillProficiencies, languageProficiencies, startingEquipment, entries, features)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', row[1:])  # Skip the original id column

    # Drop the old table and rename the temporary table
    cursor.execute('DROP TABLE backgrounds')
    cursor.execute('ALTER TABLE temp_backgrounds RENAME TO backgrounds')

    # Commit the changes
    db_connection.commit()

def main():
    conn = sqlite3.connect('game_database.db')
    reset_background_ids(conn)
    conn.close()

if __name__ == "__main__":
    main()
