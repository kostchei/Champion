import sqlite3
import json

def fetch_table_data(db_path, table_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all data from the specified table
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Get column names
    column_names = [description[0] for description in cursor.description]

    # Convert query results to a list of dictionaries
    data = [dict(zip(column_names, row)) for row in rows]

    # Close the database connection
    conn.close()

    return data

def save_json(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    db_path = 'game_database.db'
    table_name = 'monsters'
    output_path = 'monsters.json'

    # Fetch data from the table
    data = fetch_table_data(db_path, table_name)

    # Save data to JSON file
    save_json(data, output_path)

    print(f"Data from {table_name} table has been written to {output_path}")
