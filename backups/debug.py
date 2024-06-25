import sqlite3

def deduplicate_table(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Starting deduplication process...")

    # Get total number of rows before deduplication
    cursor.execute("SELECT COUNT(*) FROM UniversalEquipment")
    total_before = cursor.fetchone()[0]
    print(f"Total rows before deduplication: {total_before}")

    # Create a temporary table with unique entries
    cursor.execute("""
    CREATE TEMPORARY TABLE temp_unique AS
    SELECT MIN(ID) as ID, Name
    FROM UniversalEquipment
    GROUP BY Name COLLATE NOCASE
    """)

    # Delete all rows from the original table
    cursor.execute("DELETE FROM UniversalEquipment")

    # Insert unique entries back into the original table
    cursor.execute("""
    INSERT INTO UniversalEquipment (ID, Name)
    SELECT ID, Name FROM temp_unique
    """)

    # Get total number of rows after deduplication
    cursor.execute("SELECT COUNT(*) FROM UniversalEquipment")
    total_after = cursor.fetchone()[0]

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"Total rows after deduplication: {total_after}")
    print(f"Removed {total_before - total_after} duplicate entries.")

# Usage
db_path = 'game_database.db'
deduplicate_table(db_path)