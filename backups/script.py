import sqlite3

def rename_column(db_path):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Begin a transaction
        cursor.execute("BEGIN TRANSACTION;")

        # Fetch the original schema of the table
        cursor.execute("PRAGMA table_info(lineages);")
        columns = cursor.fetchall()

        # Define the new table schema, replacing 'lineage' with 'heritage_text'
        new_columns = []
        for column in columns:
            if column[1] == 'lineage':
                new_columns.append(f'"heritage_text" {column[2]}')
            else:
                new_columns.append(f'"{column[1]}" {column[2]}')

        # Create a new table with the updated column name
        new_table_schema = f"CREATE TABLE lineages_new ({', '.join(new_columns)});"
        cursor.execute(new_table_schema)

        # Copy data from the old table to the new table
        columns_names = [column[1] for column in columns]
        columns_names[columns_names.index('lineage')] = 'heritage_text'
        copy_data_query = f'''
            INSERT INTO lineages_new ({', '.join(columns_names)})
            SELECT {', '.join([column[1] for column in columns])}
            FROM lineages;
        '''
        cursor.execute(copy_data_query)

        # Drop the old table
        cursor.execute("DROP TABLE lineages;")

        # Rename the new table to the original table name
        cursor.execute("ALTER TABLE lineages_new RENAME TO lineages;")

        # Commit the changes
        conn.commit()

        print("Column renamed successfully.")
    
    except sqlite3.Error as e:
        # Rollback in case of any error
        conn.rollback()
        print(f"An error occurred: {e}")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    db_path = "game_database.db"  # Update with the correct path to your database file
    rename_column(db_path)
