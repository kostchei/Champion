import sqlite3
import json

# Load JSON data
with open('fighter.json', 'r') as file:
    data = json.load(file)

# Connect to SQLite database
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

# Insert or update Classes data
for cls in data['class']:
    cursor.execute('''
        INSERT INTO Classes (name, hd_number, hd_faces, proficiency, armor_proficiencies, weapon_proficiencies, skill_proficiencies, starting_equipment, gold_alternative, subclass_title)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
        hd_number=excluded.hd_number,
        hd_faces=excluded.hd_faces,
        proficiency=excluded.proficiency,
        armor_proficiencies=excluded.armor_proficiencies,
        weapon_proficiencies=excluded.weapon_proficiencies,
        skill_proficiencies=excluded.skill_proficiencies,
        starting_equipment=excluded.starting_equipment,
        gold_alternative=excluded.gold_alternative,
        subclass_title=excluded.subclass_title
    ''', (cls['name'], cls['hd']['number'], cls['hd']['faces'], json.dumps(cls['proficiency']),
          json.dumps(cls['startingProficiencies']['armor']), json.dumps(cls['startingProficiencies']['weapons']),
          json.dumps(cls['startingProficiencies']['skills']), json.dumps(cls['startingEquipment']['default']),
          cls['startingEquipment']['goldAlternative'], cls['subclassTitle']))
    class_id = cursor.execute('SELECT id FROM Classes WHERE name=?', (cls['name'],)).fetchone()[0]

    # Insert ClassFeatures data
    for feature in cls['classFeatures']:
        if isinstance(feature, str):
            print(f"Processing feature: {feature}")
            feature_parts = feature.split('|')
            if len(feature_parts) == 5:
                feature_name, feature_source, feature_page, feature_level, feature_entries = feature_parts
            elif len(feature_parts) == 4:
                feature_name, feature_source, feature_page, feature_level = feature_parts
                feature_entries = ''
            elif len(feature_parts) == 3:
                feature_name, feature_source, feature_page = feature_parts
                feature_level = 1  # Default level
                feature_entries = ''
            else:
                print(f"Unexpected format for feature: {feature}")
                continue
        elif isinstance(feature, dict):
            print(f"Processing dictionary feature with classFeature: {feature['classFeature']}")
            feature_name = feature['classFeature']
            feature_level = feature.get('level', 1)
            feature_entries = json.dumps(feature.get('entries', ''))
        
        cursor.execute('''
            INSERT INTO ClassFeatures (name, class_id, level, entries)
            VALUES (?, ?, ?, ?)
        ''', (feature_name, class_id, feature_level, feature_entries))

# Insert or update Subclasses data
for subclass in data['subclass']:
    cursor.execute('''
        INSERT INTO Subclasses (name, short_name, class_id, spellcasting_ability, caster_progression, cantrip_progression, spells_known_progression, additional_spells, subclass_table_groups)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
        short_name=excluded.short_name,
        class_id=excluded.class_id,
        spellcasting_ability=excluded.spellcasting_ability,
        caster_progression=excluded.caster_progression,
        cantrip_progression=excluded.cantrip_progression,
        spells_known_progression=excluded.spells_known_progression,
        additional_spells=excluded.additional_spells,
        subclass_table_groups=excluded.subclass_table_groups
    ''', (subclass['name'], subclass['shortName'], class_id, subclass.get('spellcastingAbility'),
          subclass.get('casterProgression'), json.dumps(subclass.get('cantripProgression')), json.dumps(subclass.get('spellsKnownProgression')),
          json.dumps(subclass.get('additionalSpells')), json.dumps(subclass.get('subclassTableGroups'))))
    subclass_id = cursor.execute('SELECT id FROM Subclasses WHERE name=?', (subclass['name'],)).fetchone()[0]

    # Insert SubclassFeatures data
    for feature in subclass['subclassFeatures']:
        if isinstance(feature, str):
            print(f"Processing subclass feature: {feature}")
            feature_parts = feature.split('|')
            if len(feature_parts) >= 4:
                feature_name = feature_parts[0]
                feature_level = feature_parts[3]
                feature_entries = feature_parts[4] if len(feature_parts) > 4 else ''
            else:
                print(f"Unexpected format for subclass feature: {feature}")
                continue
        elif isinstance(feature, dict):
            print(f"Processing dictionary subclass feature: {feature['name']}")
            feature_name = feature['name']
            feature_level = feature.get('level', 1)
            feature_entries = json.dumps(feature.get('entries', ''))
        
        cursor.execute('''
            INSERT INTO SubclassFeatures (name, class_id, subclass_id, feature_level, class, entries)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (feature_name, class_id, subclass_id, feature_level, subclass['name'], feature_entries))

# Commit changes and close the connection
conn.commit()
conn.close()
