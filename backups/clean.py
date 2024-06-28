import sqlite3
import json
from contextlib import closing

def get_db_connection():
    """ Get a database connection. """
    db_path = './game_database.db'
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def fetch_and_clean_skills_from_classes():
    """ Fetch skill proficiencies from the classes table and clean the data. """
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    cursor.execute("SELECT name, skill_proficiencies FROM classes")
    results = cursor.fetchall()

    cleaned_skills_data = {}
    for row in results:
        class_name = row['name']
        skill_proficiencies = json.loads(row['skill_proficiencies'])
        cleaned_skills_data[class_name] = skill_proficiencies

    conn.close()
    return cleaned_skills_data

def fetch_and_clean_skills_from_backgrounds():
    """ Fetch skill proficiencies from the backgrounds table and clean the data. """
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    cursor.execute("SELECT name, skillProficiencies FROM backgrounds")
    results = cursor.fetchall()

    cleaned_skills_data = {}
    for row in results:
        background_name = row['name']
        skill_proficiencies = json.loads(row['skillProficiencies'])
        cleaned_skills_data[background_name] = skill_proficiencies

    conn.close()
    return cleaned_skills_data

def update_cleaned_data(table_name, column_name, cleaned_data):
    """ Update the table with cleaned data. """
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    for name, skills in cleaned_data.items():
        cleaned_skills = json.dumps(skills)
        cursor.execute(f"UPDATE {table_name} SET {column_name} = ? WHERE name = ?", (cleaned_skills, name))
    
    conn.commit()
    conn.close()

def main():
    # Clean and update class skills
    class_skills = fetch_and_clean_skills_from_classes()
    update_cleaned_data('classes', 'skill_proficiencies', class_skills)
    print("Class skills cleaned and updated.")

    # Clean and update background skills
    background_skills = fetch_and_clean_skills_from_backgrounds()
    update_cleaned_data('backgrounds', 'skillProficiencies', background_skills)
    print("Background skills cleaned and updated.")

if __name__ == "__main__":
    main()
