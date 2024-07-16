import sqlite3
import json
import random

# Connect to the database
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

# Function to fetch monster data by ID
def get_monster_data(monster_id):
    cursor.execute("SELECT * FROM monsters WHERE id=?", (monster_id,))
    row = cursor.fetchone()
    if row:
        return {
            "id": row[0],
            "CR": row[1],
            "name": row[2],
            "type": row[3],
            "initiative": row[4],
            "AC": row[5],
            "hitpoints": row[6],
            "loot": row[7],
            "attacks": json.loads(row[8]),  # Parse the JSON formatted attacks string
            "realm": row[9]
        }
    return None

# Function to fetch character data by ID
def get_character_data(character_id):
    cursor.execute("SELECT * FROM characters WHERE id=?", (character_id,))
    row = cursor.fetchone()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "AC": row[22],  # Assuming AC is stored in column index 22
            "hitpoints": row[23],  # Assuming hitpoints are stored in column index 23
            "saves": json.loads(row[19])  # Parse the JSON formatted saves string
        }
    return None

# Function to update character status
def update_character_status(character_id, new_status):
    cursor.execute("UPDATE characters SET active=? WHERE id=?", (new_status, character_id))
    conn.commit()

# Function to simulate a d20 roll
def roll_d20():
    return random.randint(1, 20)

# Function to parse attack bonus
def parse_bonus(bonus_str):
    return int(bonus_str.strip('+'))

# Function to parse damage
def parse_damage(damage_str):
    num_dice, dice_type, bonus = damage_str.split('d')[0], damage_str.split('d')[1].split()[0], damage_str.split('+')[1].strip()
    return int(num_dice), int(dice_type), int(bonus)

# Function to resolve an attack
def resolve_attack(attack, target_ac, target_hitpoints, target_saves, condition_tracker):
    # Roll to hit
    tohit = parse_bonus(attack['tohit'])
    roll = roll_d20()
    if roll + tohit >= target_ac:
        print(f"Attack {attack['name']} hits!")
        # Roll damage
        num_dice, dice_type, bonus = parse_damage(attack['damage'])
        damage = sum(random.randint(1, dice_type) for _ in range(num_dice)) + bonus
        print(f"Damage: {damage}")
        target_hitpoints -= damage
        
        # Check for special effect
        if 'special' in attack:
            special = attack['special']
            if special['condition']:
                print(f"Special Effect: {special['effect']}")
                saving_throw = special['saving_throw']
                save_type = saving_throw['type'].lower() + '_save'
                save_dc = saving_throw['DC']
                if save_type in target_saves:
                    save_roll = roll_d20() + target_saves[save_type]
                    if save_roll < save_dc:
                        print(f"Saving throw failed! Target {saving_throw['failure']['effect']}.")
                        condition_tracker.append(saving_throw['failure']['effect'])
                        if 'additional_attack' in saving_throw['failure']:
                            additional_attack = saving_throw['failure']['additional_attack']
                            if additional_attack.get('advantage', False):
                                advantage_rolls = [roll_d20(), roll_d20()]
                                advantage_roll = max(advantage_rolls)
                                if advantage_roll + tohit >= target_ac:
                                    print(f"Additional attack hits with advantage! Rolls: {advantage_rolls}, taking the higher roll: {advantage_roll}")
                                    damage = sum(random.randint(1, dice_type) for _ in range(num_dice)) + bonus
                                    print(f"Additional Damage: {damage}")
                                    target_hitpoints -= damage
    else:
        print(f"Attack {attack['name']} misses.")

    return target_hitpoints

# Example usage
monster_id = 30
character_id = 1

monster_data = get_monster_data(monster_id)
character_data = get_character_data(character_id)

if monster_data and character_data:
    target_ac = character_data['AC']
    target_hitpoints = character_data['hitpoints']
    target_saves = character_data['saves']
    condition_tracker = []

    print(f"Character {character_data['name']} AC: {target_ac}, HP: {target_hitpoints}")
    for attack in monster_data['attacks']:
        target_hitpoints = resolve_attack(attack, target_ac, target_hitpoints, target_saves, condition_tracker)
        print(f"Remaining Hitpoints: {target_hitpoints}")
        if target_hitpoints <= 0:
            print(f"Character {character_data['name']} has been killed.")
            update_character_status(character_id, "dead")
            break

    print("Current Conditions:", condition_tracker)
else:
    print("Failed to retrieve monster or character data.")

# Close the database connection
conn.close()
