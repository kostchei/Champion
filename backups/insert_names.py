import sqlite3

def insert_names():
    names = ["Kim", "Ash", "Alex", "Bryn", "Blake", "Drew"]
    
    conn = sqlite3.connect('game_database.db')
    cursor = conn.cursor()
    
    for name in names:
        cursor.execute('INSERT INTO names (name) VALUES (?)', (name,))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    insert_names()
