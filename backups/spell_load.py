import sqlite3
import json

# File paths
db_path = 'game_database.db'
spells_json_path = 'spells.json'
sources_json_path = 'sources.json'

# Load JSON data
with open(spells_json_path, 'r') as f:
    spells_data = json.load(f)['spell']

with open(sources_json_path, 'r') as f:
    sources_data = json.load(f)

# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def convert_to_sqlite_type(value):
    if isinstance(value, (int, float, str, bool)):
        return value
    elif isinstance(value, dict):
        return json.dumps(value)
    elif value is None:
        return None
    else:
        return str(value)

# Insert spells into Spells table
for spell in spells_data:
    # Extract duration and concentration
    duration_entry = spell['duration'][0]
    duration_type = duration_entry.get('type', 'instant')
    concentration = duration_entry.get('concentration', False)
    
    if 'duration' in duration_entry:
        duration_amount = duration_entry['duration'].get('amount', '')
        duration_unit = duration_entry['duration'].get('type', '')
        duration = f"{duration_amount} {duration_unit}".strip()
    else:
        duration = duration_type
    
    # Extract casting time
    time_entry = spell['time'][0]
    casting_time = time_entry.get('unit', '')
    if 'number' in time_entry:
        casting_time = f"{time_entry['number']} {casting_time}".strip()

    # Extract range
    range_entry = spell['range']
    range_distance = range_entry.get('distance', {})
    if isinstance(range_distance, dict):
        range_amount = range_distance.get('amount', '')
        if isinstance(range_amount, int):
            range_amount = str(range_amount)
    else:
        range_amount = range_distance

    # Ensure range_amount is a string
    if isinstance(range_amount, dict):
        range_amount = json.dumps(range_amount)

    # Prepare components
    components_v = spell['components'].get('v', False)
    components_s = spell['components'].get('s', False)
    components_m = spell['components'].get('m', '')

    # Convert all values to SQLite-compatible types
    values = [
        convert_to_sqlite_type(spell['name']),
        convert_to_sqlite_type(spell.get('srd', False)),
        convert_to_sqlite_type(spell['level']),
        convert_to_sqlite_type(spell['school']),
        convert_to_sqlite_type(casting_time),
        convert_to_sqlite_type(range_entry['type']),
        convert_to_sqlite_type(range_amount),
        convert_to_sqlite_type(components_v),
        convert_to_sqlite_type(components_s),
        convert_to_sqlite_type(components_m),
        convert_to_sqlite_type(duration),
        convert_to_sqlite_type(concentration)
    ]

    # Print the values being inserted for debugging
    print(f"Inserting: {values}")
    print(f"Types: {[type(v) for v in values]}")

    try:
        cursor.execute("""
            INSERT INTO Spells (name, srd, level, school, casting_time, range_type, range_distance,
                                components_v, components_s, components_m, duration, concentration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, values)
        spell_id = cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error inserting spell {spell['name']}: {e}")
        continue

    # Insert spell entries into SpellEntries table
    for order, entry in enumerate(spell['entries']):
        try:
            cursor.execute("""
                INSERT INTO SpellEntries (spell_id, entry_order, entry_text)
                VALUES (?, ?, ?)
            """, (spell_id, order, convert_to_sqlite_type(entry)))
        except sqlite3.Error as e:
            print(f"Error inserting spell entry for {spell['name']}: {e}")
            continue

    # Insert scaling information into SpellScaling table
    if 'scalingLevelDice' in spell:
        for level, text in spell['scalingLevelDice']['scaling'].items():
            try:
                cursor.execute("""
                    INSERT INTO SpellScaling (spell_id, level, scaling_text)
                    VALUES (?, ?, ?)
                """, (spell_id, int(level), convert_to_sqlite_type(text)))
            except sqlite3.Error as e:
                print(f"Error inserting scaling for {spell['name']}: {e}")
                continue

    # Insert damage types into SpellDamageInflict table
    if 'damageInflict' in spell:
        for damage_type in spell['damageInflict']:
            try:
                cursor.execute("""
                    INSERT INTO SpellDamageInflict (spell_id, damage_type)
                    VALUES (?, ?)
                """, (spell_id, convert_to_sqlite_type(damage_type)))
            except sqlite3.Error as e:
                print(f"Error inserting damage type for {spell['name']}: {e}")
                continue

    # Insert saving throws into SpellSavingThrow table
    if 'savingThrow' in spell:
        for saving_throw in spell['savingThrow']:
            try:
                cursor.execute("""
                    INSERT INTO SpellSavingThrow (spell_id, saving_throw)
                    VALUES (?, ?)
                """, (spell_id, convert_to_sqlite_type(saving_throw)))
            except sqlite3.Error as e:
                print(f"Error inserting saving throw for {spell['name']}: {e}")
                continue

    # Insert conditions into SpellConditionInflict table
    if 'conditionInflict' in spell:
        for condition in spell['conditionInflict']:
            try:
                cursor.execute("""
                    INSERT INTO SpellConditionInflict (spell_id, condition)
                    VALUES (?, ?)
                """, (spell_id, convert_to_sqlite_type(condition)))
            except sqlite3.Error as e:
                print(f"Error inserting condition for {spell['name']}: {e}")
                continue

    # Insert area tags into SpellAreaTags table
    if 'areaTags' in spell:
        for area_tag in spell['areaTags']:
            try:
                cursor.execute("""
                    INSERT INTO SpellAreaTags (spell_id, area_tag)
                    VALUES (?, ?)
                """, (spell_id, convert_to_sqlite_type(area_tag)))
            except sqlite3.Error as e:
                print(f"Error inserting area tag for {spell['name']}: {e}")
                continue

# Insert class-specific spells from sources.json
class_tables = {
    "Bard": "BardSpells",
    "Cleric": "ClericSpells",
    "Druid": "DruidSpells",
    "Paladin": "PaladinSpells",
    "Ranger": "RangerSpells",
    "Sorcerer": "SorcererSpells",
    "Warlock": "WarlockSpells",
    "Wizard": "WizardSpells"
}

for source, spells in sources_data.items():
    for spell_name, spell_info in spells.items():
        # Get the spell_id from the Spells table
        cursor.execute("SELECT id FROM Spells WHERE name = ?", (spell_name,))
        result = cursor.fetchone()
        if result:
            spell_id = result[0]
            # Insert into class-specific spell tables
            for class_info in spell_info['class']:
                class_name = class_info['name']
                if class_name in class_tables:
                    try:
                        cursor.execute(f"""
                            INSERT INTO {class_tables[class_name]} (spell_id)
                            VALUES (?)
                        """, (spell_id,))
                    except sqlite3.Error as e:
                        print(f"Error inserting class spell for {spell_name}: {e}")
                        continue

# Commit changes and close connection
conn.commit()
conn.close()
