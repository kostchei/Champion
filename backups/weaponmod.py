import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('game_database.db')

# Read the UniversalEquipment table into a pandas DataFrame
df = pd.read_sql_query("SELECT * FROM UniversalEquipment", conn)

# List of new names to be added
new_suffixes = ["+1", "+2", "+3"]
existing_names = ["Rapier", "Longsword", "Greatsword", "Shortsword", "Battleaxe", "Greataxe"]

# Function to create new entries
def create_new_entries(df, existing_names, new_suffixes):
    new_entries = []
    max_id = df['ID'].max()

    for name in existing_names:
        existing_rows = df[df['Name'] == name]
        for suffix in new_suffixes:
            for _, row in existing_rows.iterrows():
                new_row = row.copy()
                max_id += 1
                new_row['ID'] = max_id
                new_row['Name'] = f"{suffix} {name}"
                new_entries.append(new_row)

    return pd.DataFrame(new_entries)

# Generate new entries
new_entries_df = create_new_entries(df, existing_names, new_suffixes)

# Append the new entries to the existing DataFrame
df_updated = pd.concat([df, new_entries_df], ignore_index=True)

# Update the UniversalEquipment table in the database
df_updated.to_sql('UniversalEquipment', conn, if_exists='replace', index=False)

# Commit changes and close the connection
conn.commit()
conn.close()

print("Added new entries to the UniversalEquipment table.")
