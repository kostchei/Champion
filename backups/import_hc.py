import sqlite3

def import_items(db_path):
    items = [
        "abacus", "acid (vial)", "arcane focus", "arrows", "backpack", "Battleaxe", "beast-hide cloak", "blanket",
        "block and tackle", "book", "book about plant identification", "book of arcane theory", "book of poetry",
        "bottle of black ink", "bronze discus", "bullseye lantern", "burglar's pack", "chain mail", "club",
        "common clothes", "component pouch", "costume clothes", "crossbow bolts", "crowbar", "dagger", "dart",
        "deck of cards", "deck of marked cards", "dice set", "diplomat's pack", "disguise kit", "dungeoneer's pack",
        "entertainer's pack", "explorer's pack", "Fancy Hat with Feather", "fancy leather vest", "feywild trinket",
        "fine clothes", "fishing tackle", "foot-long chain made of ten gold coins", "forgery kit", "gaming set",
        "glass bottle of unidentified slime", "gold-plated ring depicting a smiling face", "greataxe", "half-empty bottle",
        "hammer", "handaxe", "healer's kit", "herbalism kit", "holy symbol", "horn", "Horned Helmet", "hourglass",
        "hunting trap", "ink (1-ounce bottle)", "ink pen", "insignia of rank", "instrumentMusical", "iron pot",
        "javelin", "leather armor", "leather ball", 
        "ledger from your previous employer containing a small piece of useful information",
        "letter from a dead colleague posing a question you have not yet been able to answer", "light crossbow",
        "longbow", "longsword", "lucky charm", "lute", "mace", 
        "maker's mark chisel used to mark your handiwork with the symbol of the clan of crafters you learned your skill from",
        "manacles", "map of the city you grew up in", "map or scroll case", "Maul", "merchant's scale", "miner's pick",
        "oil (flask)", "pack saddle", "pair of leather boots", "past trophy", "pet mouse", "playing card set",
        "Plumed Helmet", "poorly wrought maps from your homeland that depict where you are in FaerÃ»n", "pouch",
        "prayer wheel", "priest's pack", "purse", "quarterstaff", "quill", "quiver", "rapier", "regional map",
        "Ring Mail", "ring of keys to unknown locks", "robes", "rowboat", "scale mail", "scholar's pack",
        "school uniform", "scroll containing the text of a law important to you", "scroll of pedigree",
        "scroll of your god's teachings", "set of weighted dice", "setGaming", "sheets of paper", "shield",
        "Short Sword", "shortbow", "shortsword", "shovel", "signet ring", "signet ring of an imaginary duke",
        "silk rope (50 feet)", "small article of jewelry that is distinct to your tribe", "small knife",
        "small piece of jewelry in the style of your homeland's craftsmanship", "small stone that reminds you of home",
        "spellbook", "sprig that reminds you of home", "staff", "sticks of incense", 
        "stoppered bottles filled with colored liquid", "studded leather armor",
        "the charred and twisted remains of a failed experiment",
        "the favor of an admirer (love letter, lock of hair, or trinket)", "the skull of a boar", "thieves' tools",
        "three-dragon ante set", "token of the life you once knew", "token to remember your parents by", "toolArtisan",
        "traveler's clothes", "trinket", "trophy from an animal you killed", "trophy taken from a fallen enemy",
        "two-person tent", "uniform in the style of your unit and indicative of your rank", "vestments",
        "vial of fish scales", "vial of jellyfish stingers", "vial of seaweed", "vizier's cartouche", "warhammer",
        "whetstone", "whip"
    ]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if UniversalEquipment table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='UniversalEquipment'")
    if not cursor.fetchone():
        print("Error: UniversalEquipment table does not exist in the database.")
        conn.close()
        return

    # Get existing columns in UniversalEquipment table
    cursor.execute("PRAGMA table_info(UniversalEquipment)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'Name' not in columns:
        print("Error: 'Name' column does not exist in UniversalEquipment table.")
        conn.close()
        return

    print(f"Columns in UniversalEquipment table: {columns}")

    # Create a temporary table for case-insensitive comparison
    cursor.execute("""
    CREATE TEMPORARY TABLE temp_items (
        name TEXT COLLATE NOCASE
    )
    """)

    # Insert existing items into the temporary table
    cursor.execute("""
    INSERT INTO temp_items (name)
    SELECT Name FROM UniversalEquipment
    """)
    
    print(f"Loaded {cursor.rowcount} existing items into temporary table.")

    # Insert new items
    new_items = 0
    existing_items = 0

    for item_name in items:
        # Check if item exists (case-insensitive)
        cursor.execute("SELECT name FROM temp_items WHERE name = ?", (item_name,))
        if cursor.fetchone() is None:
            # Item doesn't exist, insert it
            try:
                cursor.execute("INSERT INTO UniversalEquipment (Name) VALUES (?)", (item_name,))
                cursor.execute("INSERT INTO temp_items (name) VALUES (?)", (item_name,))
                new_items += 1
                print(f"Added new item: {item_name}")
            except sqlite3.Error as e:
                print(f"Error inserting item '{item_name}': {e}")
        else:
            existing_items += 1
            print(f"Item already exists: {item_name}")

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"\nImport complete.")
    print(f"Total items processed: {len(items)}")
    print(f"New items added: {new_items}")
    print(f"Existing items: {existing_items}")

# Usage
db_path = 'game_database.db'
import_items(db_path)