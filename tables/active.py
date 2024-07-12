import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

# Add the 'active' column to the 'characters' table if it does not already exist
cursor.execute('''
    ALTER TABLE characters
    ADD COLUMN active TEXT
''')

# Add a trigger to ensure the 'active' column only contains "true", "false", "dead", or NULL
cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS validate_active_value
    BEFORE INSERT OR UPDATE ON characters
    FOR EACH ROW
    BEGIN
        SELECT
            CASE
                WHEN NEW.active IS NOT NULL AND NEW.active NOT IN ('true', 'false', 'dead') THEN
                    RAISE (ABORT, 'Invalid value for active column')
            END;
    END;
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
