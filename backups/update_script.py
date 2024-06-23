import sqlite3
import csv

def read_csv(csv_path):
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        return [row['id'] for row in reader]

def update_backgrounds_table(db_path, csv_path):
    # Read the CSV file to get the list of current backgrounds
    current_backgrounds = read_csv(csv_path)

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add the 'campaign_specific' column if it doesn't exist
    cursor.execute("PRAGMA table_info(backgrounds)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'campaign_specific' not in columns:
        cursor.execute("ALTER TABLE backgrounds ADD COLUMN campaign_specific BOOLEAN")

    # Set all campaign_specific to 0 initially
    cursor.execute("UPDATE backgrounds SET campaign_specific = 0")

    # Update 'campaign_specific' column to 1 for backgrounds in the CSV
    cursor.executemany("UPDATE backgrounds SET campaign_specific = 1 WHERE id = ?", [(id,) for id in current_backgrounds])

    # Delete backgrounds that are not in the CSV file
    cursor.execute("DELETE FROM backgrounds WHERE id NOT IN ({})".format(','.join('?' for _ in current_backgrounds)), current_backgrounds)

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Usage
db_path = 'game_database.db'  # Adjust the path to your database
csv_path = 'backgrounds_update.csv'  # Adjust the path to your CSV file
update_backgrounds_table(db_path, csv_path)
