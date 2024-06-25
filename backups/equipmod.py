import sqlite3

# Connect to your SQLite database
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

# Function to check if a column exists
def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [info[1] for info in cursor.fetchall()]
    return column_name in columns

# List of columns to add
columns_to_add = {
    "ID": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "Name": "VARCHAR(255)",
    "Item_Type": "VARCHAR(255)",
    "Base_Weight": "FLOAT",
    "Base_Value": "FLOAT",
    "Damage": "VARCHAR(255)",
    "Range": "VARCHAR(255)",
    "Charges": "INT",
    "Description": "TEXT",
    "Weapon_Category": "VARCHAR(255)",
    "Age": "VARCHAR(255)",
    "Property": "TEXT",
    "Dmg_Type": "VARCHAR(255)",
    "Firearm": "BOOLEAN",
    "Weapon": "BOOLEAN",
    "Ammo_Type": "VARCHAR(255)",
    "Arrow": "BOOLEAN",
    "Pack_Contents": "TEXT",
    "Axe": "BOOLEAN",
    "Armor": "BOOLEAN",
    "AC": "INT",
    "Strength": "VARCHAR(255)",
    "Stealth": "BOOLEAN",
    "Club": "BOOLEAN",
    "Bolt": "BOOLEAN",
    "Scf_Type": "VARCHAR(255)",
    "Dagger": "BOOLEAN",
    "Sword": "BOOLEAN",
    "Bonus_Spell_Attack": "VARCHAR(255)",
    "Bonus_Spell_Save_DC": "VARCHAR(255)",
    "Req_Attune": "VARCHAR(255)",
    "Req_Attune_Tags": "TEXT",
    "Focus": "TEXT",
    "Wondrous": "BOOLEAN",
    "Weight": "FLOAT",
    "Bonus_Weapon": "VARCHAR(255)",
    "Type": "VARCHAR(255)",
    "Tier": "VARCHAR(255)",
    "Loot_Tables": "TEXT"
}

# Add missing columns
for column, col_type in columns_to_add.items():
    if not column_exists(cursor, 'UniversalEquipment', column):
        cursor.execute(f"ALTER TABLE UniversalEquipment ADD COLUMN {column} {col_type};")

# Commit and close the connection
conn.commit()
conn.close()
