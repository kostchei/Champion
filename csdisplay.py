import json
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import os

BUFF_OFF_WHITE = "#F7F6ED"
DARK_BLUE = "#1E2832"
WHITE = "#EDF3FC"
GREY = "#F0F0E6"

def clean_nested_fields(data, nested_keys):
    for key in nested_keys:
        if key in data:
            del data[key]

def save_character(character_data):
    if 'features' in character_data:
        clean_nested_fields(character_data['features'], [k for k in character_data['features'] if 'choices' in character_data['features'][k]])
    if 'class_equipment' in character_data:
        clean_nested_fields(character_data['class_equipment'], ['options', 'choice'])
    if 'class_features' in character_data:
        clean_nested_fields(character_data['class_features'], [k for k in character_data['class_features'] if 'choices' in character_data['class_features'][k]])

    keys_to_rename = {k: k.replace("default_", "chosen_") for k in character_data if k.startswith("default_")}
    for old_key, new_key in keys_to_rename.items():
        character_data[new_key] = character_data.pop(old_key)

    character_name = character_data['name']
    realm = realm_var.get() or "tier_1"
    filename = f"./saves/{character_name}.{realm}.json"
    with open(filename, 'w') as f:
        json.dump(character_data, f, indent=4)
    messagebox.showinfo("Saved", f"Character saved as {filename}")

def choose_realm():
    realms = [f.split('.')[0] for f in os.listdir("./realms") if f.endswith(".json")]
    selected_realm = RealmSelectionDialog(root, realms).show()
    if selected_realm:
        realm_var.set(selected_realm)

def get_class_details(class_name):
    with open(f'./classes/{class_name}.json', 'r') as file:
        return json.load(file)

def calculate_skill_and_saving_throw_bonuses(character_data):
    proficiency_bonus = character_data['proficiency_bonus']
    saving_throws = character_data.get("saving_throws", [])
    skills = {
        "Strength": ["Athletics"], "Intelligence": ["Arcana", "History", "Investigation", "Nature", "Religion"],
        "Wisdom": ["Animal Handling", "Insight", "Medicine", "Perception", "Survival"], "Dexterity": ["Acrobatics", "Sleight of Hand", "Stealth"],
        "Constitution": [], "Charisma": ["Deception", "Intimidation", "Performance", "Persuasion"]
    }
    saving_throws_dict = {
        "Str Save": "strength", "Int Save": "intelligence", "Wis Save": "wisdom",
        "Dex Save": "dexterity", "Con Save": "constitution", "Cha Save": "charisma"
    }
    
    for attribute, skill_list in skills.items():
        for skill in skill_list:
            skill_key = skill.lower().replace(" ", "_")
            attribute_key = attribute.lower()
            modifier = character_data[f"{attribute_key}_modifier"]
            if skill in set(character_data.get("skills", [])).union(set(character_data.get("class_skills", []))):
                character_data[f"{skill_key}_bonus"] = modifier + proficiency_bonus
            else:
                character_data[f"{skill_key}_bonus"] = modifier

    for save, attribute in saving_throws_dict.items():
        attribute_key = attribute.lower()
        modifier = character_data[f"{attribute_key}_modifier"]
        if save in saving_throws:
            character_data[f"{save.lower().replace(' ', '_')}_bonus"] = modifier + proficiency_bonus
        else:
            character_data[f"{save.lower().replace(' ', '_')}_bonus"] = modifier

def apply_fighting_style_bonuses(character_data):
    chosen_fighting_style = character_data.get('chosen_fighting_style', {})
    if chosen_fighting_style.get('name') == "Defense":
        character_data['armor_class'] += 1
    elif chosen_fighting_style.get('name') == "Dueling":
        if 'attack' in character_data:
            character_data['attack']['damage'] += " + 2"

def choose_class_features(character_data):
    features = get_class_details(character_data['class']).get('features', {})
    for feature_name, feature_details in features.items():
        if isinstance(feature_details, dict) and 'choices' in feature_details:
            chosen_feature = FeatureSelectionDialog(root, f"Choose {feature_name}", feature_name, feature_details['choices']).show()
            if chosen_feature:
                character_data[f"chosen_{feature_name.lower().replace(' ', '_')}"] = chosen_feature
            else:
                messagebox.showerror("Invalid Choice", f"You must choose a valid {feature_name}.")
        else:
            character_data[f"chosen_{feature_name.lower().replace(' ', '_')}"] = feature_details
    
    if 'features' in character_data:
        clean_nested_fields(character_data['features'], [k for k in character_data['features'] if 'choices' in character_data['features'][k]])
    apply_fighting_style_bonuses(character_data)
    save_character(character_data)
    update_character_sheet(character_data)

class FeatureSelectionDialog(tk.Toplevel):
    def __init__(self, parent, title, feature_name, feature_choices):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x200")
        self.feature_name = feature_name
        self.selected_feature = None
        self.feature_choices = feature_choices

        tk.Label(self, text=f"Choose one of the following {feature_name}:", font=("Arial", 12)).pack(pady=10)
        self.var = tk.StringVar(self)
        feature_display = [f"{choice['name']}: {choice['description']}" for choice in feature_choices]
        self.dropdown = ttk.Combobox(self, textvariable=self.var, values=feature_display)
        self.dropdown.pack(pady=10)
        tk.Button(self, text="OK", command=self.on_select).pack(pady=10)

    def on_select(self):
        selected_index = self.dropdown.current()
        self.selected_feature = self.feature_choices[selected_index] if selected_index != -1 else None
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.wait_window()
        return self.selected_feature

class RealmSelectionDialog(tk.Toplevel):
    def __init__(self, parent, options):
        super().__init__(parent)
        self.title("Choose Realm")
        self.geometry("300x100")
        self.var = tk.StringVar(self)
        self.var.set(options[0])
        tk.Label(self, text="Choose a realm:").pack(pady=10)
        self.dropdown = ttk.Combobox(self, textvariable=self.var, values=options)
        self.dropdown.pack(pady=5)
        tk.Button(self, text="OK", command=self.on_select).pack(pady=5)

    def on_select(self):
        self.selected_option = self.var.get()
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.wait_window()
        return getattr(self, "selected_option", None)

class SkillSelectionDialog(tk.Toplevel):
    def __init__(self, parent, title, skill_choices, num_skills):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x300")
        self.selected_skills = []
        tk.Label(self, text=f"Choose {num_skills} skills:", font=("Arial", 12)).pack(pady=10)
        self.var = tk.StringVar(self)
        self.listbox = tk.Listbox(self, selectmode=tk.MULTIPLE, exportselection=0)
        for skill in skill_choices:
            self.listbox.insert(tk.END, skill)
        self.listbox.pack(pady=10)
        tk.Button(self, text="OK", command=self.on_select).pack(pady=10)

    def on_select(self):
        selected_indices = self.listbox.curselection()
        self.selected_skills = [self.listbox.get(i) for i in selected_indices]
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.wait_window()
        return self.selected_skills

def choose_class_skills(character_data):
    class_details = get_class_details(character_data['class'])
    skill_options = set(class_details['skills']['options'])
    num_skills = class_details['skills']['number_skills']
    available_skills = skill_options - set(character_data.get("skills", []))
    chosen_skills = SkillSelectionDialog(root, "Choose Class Skills", list(available_skills), num_skills).show()
    if len(chosen_skills) == num_skills:
        character_data['class_skills'] = chosen_skills
        calculate_skill_and_saving_throw_bonuses(character_data)
    else:
        messagebox.showerror("Invalid Choice", f"You must choose exactly {num_skills} skills.")
    save_character(character_data)
    update_character_sheet(character_data)

def display_character_sheet(character_data):
    global root, realm_var
    root = tk.Tk()
    root.title("Character Sheet")
    root.geometry("1200x1400")
    root.configure(bg=BUFF_OFF_WHITE)
    canvas = tk.Canvas(root, bg=BUFF_OFF_WHITE)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
    scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    global main_frame
    main_frame = tk.Frame(canvas, bg=BUFF_OFF_WHITE)
    canvas.create_window((0, 0), window=main_frame, anchor="nw")
    render_character_sheet(character_data)
    realm_var = tk.StringVar(value="tier_1")
    root.mainloop()

def render_character_sheet(character_data):
    for widget in main_frame.winfo_children():
        widget.destroy()
    details_frame = tk.Frame(main_frame, bg=BUFF_OFF_WHITE)
    details_frame.grid(row=0, column=0, columnspan=4, sticky="nsew")

    if 'current_hp' not in character_data:
        character_data['current_hp'] = character_data['hit_points']

    details = [
        ("Character Name", character_data['name']), ("Gender", character_data['gender']),
        ("Game Edition", character_data['game_edition']), ("Race", character_data['race']),
        ("Class", character_data['class']), ("Background", character_data['background']),
        ("Proficiency Bonus", character_data['proficiency_bonus']), 
        ("Experience", character_data['experience_points']), ("Level", f"Level {character_data['level']}"),
        ("Hit Points", character_data['hit_points']), 
        ("Current HP", character_data['current_hp']),
        ("Armor Class", character_data.get('armor_class', 'None'))
    ]

    for i, (label, value) in enumerate(details):
        row, col = divmod(i, 4)
        tk.Label(details_frame, text=f"{label}:", font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row, column=col*2, sticky="w", padx=10, pady=5)
        tk.Label(details_frame, text=value, font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row, column=col*2 + 1, sticky="w", padx=10, pady=5)

    main_frame.columnconfigure(0, weight=1, minsize=300)
    main_frame.columnconfigure(1, weight=1, minsize=200)
    main_frame.columnconfigure(2, weight=1, minsize=400)
    main_frame.columnconfigure(3, weight=1, minsize=200)

    attributes_frame = tk.Frame(main_frame, bg=BUFF_OFF_WHITE)
    attributes_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

    attributes_skills = {
        "Strength": ["Str Save", "Athletics"], "Intelligence": ["Int Save", "Arcana", "History", "Investigation", "Nature", "Religion"],
        "Wisdom": ["Wis Save", "Animal Handling", "Insight", "Medicine", "Perception", "Survival"], "Dexterity": ["Dex Save", "Acrobatics", "Sleight of Hand", "Stealth"],
        "Constitution": ["Con Save"], "Charisma": ["Cha Save", "Deception", "Intimidation", "Performance", "Persuasion"]
    }
    
    row_offset = 0
    for attribute, skills in attributes_skills.items():
        attribute_value = character_data[attribute.lower()]
        attribute_modifier = character_data[f"{attribute.lower()}_modifier"]
        tk.Label(attributes_frame, text=f"{attribute}:", font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row_offset, column=0, sticky="w", padx=10, pady=5)
        tk.Label(attributes_frame, text=f"{attribute_value} ({attribute_modifier:+})", font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row_offset, column=1, sticky="w", padx=10, pady=5)
        row_offset += 1
        for skill in skills:
            skill_key = skill.lower().replace(" ", "_")
            bullet = "●" if skill in set(character_data.get("skills", [])).union(set(character_data.get("class_skills", []))) else "○"
            skill_bonus = character_data.get(f"{skill_key}_bonus", 0)
            tk.Label(attributes_frame, text=f"{bullet} {skill} ({skill_bonus:+})", font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).grid(row=row_offset, column=1, sticky="w", padx=10, pady=2)
            row_offset += 1

    list_frame = tk.Frame(main_frame, bg=BUFF_OFF_WHITE)
    list_frame.grid(row=1, column=2, sticky="nsew")
    def create_readonly_listbox(parent, title, items):
        tk.Label(parent, text=title, font=("Arial", 14), bg=BUFF_OFF_WHITE, fg=DARK_BLUE).pack(anchor="w", padx=10, pady=5)
        listbox = tk.Listbox(parent, height=len(items), width=30, bg=WHITE, fg=DARK_BLUE, font=("Arial", 14))
        for item in items:
            listbox.insert(tk.END, item)
        listbox.pack(anchor="w", padx=10, pady=2)
        listbox.config(state=tk.DISABLED)

    attack_info = [f'{character_data["attack"]["name"]}, {character_data["attack"]["to_hit"]} to hit, {character_data["attack"]["damage"]}'] if "attack" in character_data else []
    create_readonly_listbox(list_frame, "Attack", attack_info)
    class_features = [f"{v.get('name', '')}: {v.get('description', '')}\nEffect: {v.get('effect', '')}" for k, v in character_data.items() if k.startswith("chosen_") and isinstance(v, dict)]
    create_readonly_listbox(list_frame, "Class Features", class_features)
    create_readonly_listbox(list_frame, "Reputation", character_data.get("reputation", []))
    create_readonly_listbox(list_frame, "Equipment", character_data.get("equipment", []))
    create_readonly_listbox(list_frame, "Unassigned Skills", list(set(character_data.get("skills", [])).union(set(character_data.get("class_skills", [])))))

    actions_frame = tk.Frame(main_frame, bg=BUFF_OFF_WHITE)
    actions_frame.grid(row=1, column=3, sticky="nsew")
    tk.Button(actions_frame, text="Save Changes", command=lambda: [calculate_skill_and_saving_throw_bonuses(character_data), save_character(character_data)], bg=GREY, fg=DARK_BLUE).pack(pady=10)
    tk.Button(actions_frame, text="Choose Class Features", command=lambda: choose_class_features(character_data), bg=GREY, fg=DARK_BLUE).pack(pady=10)
    tk.Button(actions_frame, text="Choose Class Skills", command=lambda: choose_class_skills(character_data), bg=GREY, fg=DARK_BLUE).pack(pady=10)
    tk.Button(actions_frame, text="Choose Realm", command=choose_realm, bg=GREY, fg=DARK_BLUE).pack(pady=10)

def update_character_sheet(character_data):
    render_character_sheet(character_data)

if __name__ == "__main__":
    input_file = sys.argv[1]
    with open(input_file, 'r') as f:
        character_data = json.load(f)
    calculate_skill_and_saving_throw_bonuses(character_data)
    if 'current_hp' not in character_data:
        character_data['current_hp'] = character_data['hit_points']
    display_character_sheet(character_data)
