import sqlite3

def rename_entries_to_race_traits(db_connection):
    cursor = db_connection.cursor()
    
    # Drop the existing race_traits table if it exists
    cursor.execute('DROP TABLE IF EXISTS race_traits')
    
    # Rename the entries table to race_traits
    cursor.execute('ALTER TABLE entries RENAME TO race_traits')
    
    db_connection.commit()

def main():
    conn = sqlite3.connect('game_database.db')
    rename_entries_to_race_traits(conn)
    conn.close()

if __name__ == "__main__":
    main()
