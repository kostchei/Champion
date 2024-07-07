import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('game_database.db')

# Read the UniversalEquipment table into a pandas DataFrame
df = pd.read_sql_query("SELECT * FROM UniversalEquipment", conn)

# Convert the ID column to numeric, coercing errors
df['ID'] = pd.to_numeric(df['ID'], errors='coerce')

# Drop rows where ID could not be converted to a number
df.dropna(subset=['ID'], inplace=True)

# Ensure ID is an integer
df['ID'] = df['ID'].astype(int)

# Function to generate unique IDs
def make_unique_ids(df, id_column):
    id_counts = df[id_column].value_counts()
    duplicates = id_counts[id_counts > 1].index

    for dup_id in duplicates:
        duplicate_rows = df[df[id_column] == dup_id]
        new_ids = range(df[id_column].max() + 1, df[id_column].max() + 1 + len(duplicate_rows) - 1)
        df.loc[duplicate_rows.index[1:], id_column] = new_ids

    return df

# Apply the function to make IDs unique
df_unique = make_unique_ids(df, 'ID')  # Use the correct column name

# Update the UniversalEquipment table in the database
df_unique.to_sql('UniversalEquipment', conn, if_exists='replace', index=False)

# Commit changes and close the connection
conn.commit()
conn.close()

print("Updated UniversalEquipment table with unique IDs.")
