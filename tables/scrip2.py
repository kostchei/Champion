import sqlite3

def add_desc_text_column(db_path):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(backgrounds);")
        columns = [info[1] for info in cursor.fetchall()]
        if 'desc_text' not in columns:
            # Add the new column to the backgrounds table
            cursor.execute("ALTER TABLE backgrounds ADD COLUMN desc_text TEXT;")
            print("Column 'desc_text' added successfully.")
        else:
            print("Column 'desc_text' already exists.")
        
        # Commit the changes and close the connection
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    db_path = "game_database.db"  # Update with the correct path to your database file
    add_desc_text_column(db_path)
