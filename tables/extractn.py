import sqlite3

def export_names_to_text_file(db_path, output_file):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query to select all names from the backgrounds table
        query = "SELECT name FROM backgrounds"
        cursor.execute(query)

        # Fetch all names
        names = cursor.fetchall()

        # Write names to the output file
        with open(output_file, 'w') as file:
            for name in names:
                file.write(name[0] + '\n')

        print(f"Successfully exported names to {output_file}")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

# Specify the path to your database and the output file
db_path = 'game_database.db'
output_file = 'background_names.txt'

# Call the function to export names
export_names_to_text_file(db_path, output_file)
