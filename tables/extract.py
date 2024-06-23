import sqlite3
import csv
import os

def extract_lineages_subraces_to_csv(db_path, csv_path):
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.OperationalError as e:
        print(f"Error: Unable to open database file. {e}")
        return

    cursor = conn.cursor()

    # Extract lineages
    cursor.execute('''
    SELECT id, name, "lineage" AS type, game_edition_id FROM lineages
    ''')
    lineages = cursor.fetchall()

    # Extract subraces
    cursor.execute('''
    SELECT id, name, "subrace" AS type, game_edition_id FROM subraces
    ''')
    subraces = cursor.fetchall()

    combined = lineages + subraces

    # Write to CSV
    with open(csv_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['id', 'name', 'type', 'game_edition_id'])
        csvwriter.writerows(combined)

    conn.close()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    db_path = os.path.join(script_dir, 'game_database.db')
    csv_path = os.path.join(script_dir, 'lineages_subraces.csv')
    extract_lineages_subraces_to_csv(db_path, csv_path)
    print(f"Combined list exported to {csv_path}")

