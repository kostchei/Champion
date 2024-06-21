import sqlite3

def create_realms_table():
    conn = sqlite3.connect('game_database.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS realms (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        style TEXT,
        level_range TEXT,
        environment_type TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS realm_characters (
        realm_id INTEGER,
        character_id INTEGER,
        PRIMARY KEY(realm_id, character_id),
        FOREIGN KEY(realm_id) REFERENCES realms(id),
        FOREIGN KEY(character_id) REFERENCES characters(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS realm_equipment (
        realm_id INTEGER,
        equipment_id INTEGER,
        PRIMARY KEY(realm_id, equipment_id),
        FOREIGN KEY(realm_id) REFERENCES realms(id),
        FOREIGN KEY(equipment_id) REFERENCES equipment(id)
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_realms_table()
