import sqlite3

def delete_entries_with_no_skills(db_connection):
    cursor = db_connection.cursor()
    cursor.execute('''
        DELETE FROM backgrounds
        WHERE skillProficiencies = '[]'
    ''')
    db_connection.commit()

def main():
    conn = sqlite3.connect('game_database.db')
    delete_entries_with_no_skills(conn)
    conn.close()

if __name__ == "__main__":
    main()
