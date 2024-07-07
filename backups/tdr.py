import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('game_database.db')

# Read the UniversalEquipment table into a pandas DataFrame
df = pd.read_sql_query("SELECT * FROM UniversalEquipment", conn)

# Print column names and first few rows to inspect the data
print("Columns in UniversalEquipment table:")
print(df.columns)
print("\nFirst few rows of the table:")
print(df.head())

conn.close()
