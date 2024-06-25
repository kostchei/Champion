import sqlite3
import json

# Load JSON data
with open('class-sidekick.json', 'r') as file:
    data = json.load(file)

# Connect to SQLite database
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

# Insert or update Classes data
for cls in data['class']:
    starting_proficiencies = cls.get('startingProficiencies', {})
    starting_equipment = cls.get('startingEquipment', {}).get('default', [])

    cursor.execute('''
        INSERT INTO Classes (name, game_edition, primary_stat, secondary_stat, hd_faces, proficiency, armor_proficiencies, weapon_proficiencies, skill_proficiencies, starting_equipment, subclass_title, tertiary_stat, dump_stat, flavour_text)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
        game_edition=excluded.game_edition,
        primary_stat=excluded.primary_stat,
        secondary_stat=excluded.secondary_stat,
        hd_faces=excluded.hd_faces,
        proficiency=excluded.proficiency,
        armor_proficiencies=excluded.armor_proficiencies,
        weapon_proficiencies=excluded.weapon_proficiencies,
        skill_proficiencies=excluded.skill_proficiencies,
        starting_equipment=excluded.starting_equipment,
        subclass_title=excluded.subclass_title,
        tertiary_stat=excluded.tertiary_stat,
        dump_stat=excluded.dump_stat,
        flavour_text=excluded.flavour_text
    ''', (cls['name'], 
          cls.get('gameEdition'), 
          cls.get('primaryStat'), 
          cls.get('secondaryStat'), 
          cls.get('hd', {}).get('faces'), 
          json.dumps(cls.get('proficiency', [])),
          json.dumps(starting_proficiencies.get('armor', [])), 
          json.dumps(starting_proficiencies.get('weapons', [])),
          json.dumps(starting_proficiencies.get('skills', [])), 
          json.dumps(starting_equipment),
          cls.get('subclassTitle', ''),  # Default to empty string if not present
          cls.get('tertiaryStat'), 
          cls.get('dumpStat'), 
          cls.get('flavourText')))
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

# Check if 'subclass' key exists in the JSON data
if 'subclass' in data:
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
