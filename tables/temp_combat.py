# /tables/temp_combat.py
import sqlite3
import json
import random

# Connect to the database
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

# Function to add a combatant
def add_combatant(name, type, ac, hitpoints, conditions, attack_data):
    cursor.execute('''
        INSERT INTO combatants (name, type, ac, hitpoints, conditions, attack_data)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, type, ac, hitpoints, json.dumps(conditions), json.dumps(attack_data)))
    conn.commit()

# Function to fetch combatant data by ID
def get_combatant_data(combatant_id):
    cursor.execute("SELECT * FROM combatants WHERE id=?", (combatant_id,))
    row = cursor.fetchone()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "ac": row[3],
            "hitpoints": row[4],
            "conditions": json.loads(row[5]),
            "attack_data": json.loads(row[6])
        }
    return None

# Function to update combatant conditions and hitpoints
def update_combatant_status(combatant_id, hitpoints, conditions):
    cursor.execute('''
        UPDATE combatants
        SET hitpoints = ?, conditions = ?
        WHERE id = ?
    ''', (hitpoints, json.dumps(conditions), combatant_id))
    conn.commit()

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

# Function to determine if an attack has advantage, disadvantage, or neither
def determine_attack_roll(condition_tracker):
    rolls = [roll_d20()]
    if 'advantage' in condition_tracker:
        rolls.append(roll_d20())
        return max(rolls)
    elif 'disadvantage' in condition_tracker:
        rolls.append(roll_d20())
        return min(rolls)
    return rolls[0]

# Function to handle pre-attack conditions
def apply_pre_attack_conditions(attacker_conditions, defender_conditions):
    condition_tracker = []
    if 'pack_tactics' in attacker_conditions:
        condition_tracker.append('advantage')
    if 'prone' in defender_conditions:
        condition_tracker.append('advantage')
    if 'blinded' in attacker_conditions:
        condition_tracker.append('disadvantage')
    return condition_tracker

# Function to handle post-attack conditions
def apply_post_attack_conditions(attack, target_saves, condition_tracker, target_hitpoints):
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
                        additional_hit = roll_d20()
                        if additional_attack.get('advantage', False):
                            additional_hit = determine_attack_roll(['advantage'])
                        if additional_hit + parse_bonus(additional_attack['tohit']) >= target_ac:
                            print(f"Additional attack hits! Roll: {additional_hit}")
                            num_dice, dice_type, bonus = parse_damage(additional_attack['damage'])
                            damage = sum(random.randint(1, dice_type) for _ in range(num_dice)) + bonus
                            print(f"Additional Damage: {damage}")
                            target_hitpoints -= damage
    return target_hitpoints

# Function to resolve an attack with critical hits
def resolve_attack(attack, target_ac, target_hitpoints, target_saves, attacker_conditions, defender_conditions):
    condition_tracker = apply_pre_attack_conditions(attacker_conditions, defender_conditions)
    tohit = parse_bonus(attack['tohit'])
    roll = determine_attack_roll(condition_tracker)
    is_critical = False

    # Check for critical hit
    if roll == 20:
        is_critical = True
    elif roll >= 19 and 'improved critical 19' in attacker_conditions:
        is_critical = True
    elif roll >= 18 and 'improved critical 18' in attacker_conditions:
        is_critical = True

    if roll + tohit >= target_ac:
        print(f"Attack {attack['name']} hits!")
        num_dice, dice_type, bonus = parse_damage(attack['damage'])

        # Double the dice for critical hit
        if is_critical:
            num_dice *= 2
            print(f"Critical hit! Rolling {num_dice}d{dice_type} for damage.")

        damage = sum(random.randint(1, dice_type) for _ in range(num_dice)) + bonus
        print(f"Damage: {damage}")
        target_hitpoints -= damage
        target_hitpoints = apply_post_attack_conditions(attack, target_saves, condition_tracker, target_hitpoints)
    else:
        print(f"Attack {attack['name']} misses.")
    return target_hitpoints, condition_tracker


# Example usage
monster_id = 30
character_id = 1

# Assuming combatants table already exists and is being used here
# Fetch monster and character data
monster_data = get_monster_data(monster_id)
character_data = get_character_data(character_id)

if monster_data and character_data:
    # Add combatants to the combatants table
    add_combatant(monster_data['name'], 'monster', monster_data['AC'], monster_data['hitpoints'], [], monster_data['attacks'])
    add_combatant(character_data['name'], 'character', character_data['AC'], character_data['hitpoints'], [], [])

    # Fetch combatant data
    monster_combatant = get_combatant_data(1)  # Assuming monster is the first entry
    character_combatant = get_combatant_data(2)  # Assuming character is the second entry

    target_ac = character_combatant['ac']
    target_hitpoints = character_combatant['hitpoints']
    target_saves = character_data['saves']
    attacker_conditions = []  # Add actual conditions from the attacker's state
    defender_conditions = character_combatant['conditions']

    print(f"Character {character_combatant['name']} AC: {target_ac}, HP: {target_hitpoints}")
    for attack in monster_combatant['attack_data']:
        target_hitpoints, new_conditions = resolve_attack(attack, target_ac, target_hitpoints, target_saves, attacker_conditions, defender_conditions)
        defender_conditions.extend(new_conditions)
        update_combatant_status(character_combatant['id'], target_hitpoints, defender_conditions)
        print(f"Remaining Hitpoints: {target_hitpoints}")
        if target_hitpoints <= 0:
            print(f"Character {character_combatant['name']} has been killed.")
            update_character_status(character_id, "dead")
            break

    print("Current Conditions:", defender_conditions)
else:
    print("Failed to retrieve monster or character data.")

# Close the database connection
conn.close()
