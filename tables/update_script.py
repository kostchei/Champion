import csv
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('game_database.db')  # Replace with your database file path
cursor = conn.cursor()

# Read the CSV file
with open('update_lineages.csv', 'r') as file:
    csv_reader = csv.DictReader(file)
    
    # Prepare the update query
    update_query = '''
    UPDATE lineages
    SET game_edition_id = ?
    WHERE id = ? AND game_edition_id IS NULL
    '''
    
    # Iterate through the CSV rows and update the database
    for row in csv_reader:
        lineage_id = row['id']
        game_edition_id = row['game_edition_id']
        
        # Only update if game_edition_id is not empty
        if game_edition_id:
            cursor.execute(update_query, (game_edition_id, lineage_id))

    # Commit the changes
    conn.commit()

# Close the database connection
conn.close()

print("Database update completed.")
