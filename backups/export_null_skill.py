import sqlite3
import csv

def query_backgrounds_no_skills(db_connection, csv_file):
    cursor = db_connection.cursor()
    cursor.execute('''
        SELECT * FROM backgrounds
        WHERE skillProficiencies = '[]'
    ''')

    rows = cursor.fetchall()

    # Get the column names
    column_names = [description[0] for description in cursor.description]

    # Write to CSV
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(column_names)  # Write the header
        writer.writerows(rows)  # Write the data

def main():
    conn = sqlite3.connect('game_database.db')
    query_backgrounds_no_skills(conn, 'backgrounds_no_skills.csv')
    conn.close()

if __name__ == "__main__":
    main()
