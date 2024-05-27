import json
import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle

BUFF_OFF_WHITE = (247/255, 246/255, 237/255, 1)
DARK_BLUE = (30/255, 40/255, 50/255, 1)
WHITE = (237/255, 243/255, 252/255, 1)
GREY = (240/255, 240/255, 230/255, 1)
FONT_SIZE = '12sp'

class CharacterSheet(BoxLayout):
    def __init__(self, character_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.character_data = character_data

        # Set window size
        self.size_hint = (None, None)
        self.size = (960, 1080)

        # Light theme setup
        with self.canvas.before:
            Color(*BUFF_OFF_WHITE)  # Light background
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
            self.bind(pos=self.update_rect, size=self.update_rect)

        # Scrollable content
        scroll_view = ScrollView(size_hint=(1, None), size=(960, 1080))
        main_layout = GridLayout(cols=1, size_hint_y=None, padding=20, spacing=20)
        main_layout.bind(minimum_height=main_layout.setter('height'))

        # Top section for character details
        top_layout = GridLayout(cols=4, size_hint_y=None, height=100, spacing=10, padding=20)
        top_details = [
            ("Character Name", character_data['name']),
            ("Class & Level", ""),  # Placeholder
            ("Background", character_data['background']),
            ("Race", character_data['race']),
            ("Alignment", ""),  # Placeholder
            ("Experience Points", "")  # Placeholder
        ]
        for label, value in top_details:
            top_layout.add_widget(Label(text=label, font_size=FONT_SIZE, size_hint_y=None, height=30, color=DARK_BLUE))
            top_layout.add_widget(TextInput(text=str(value), font_size=FONT_SIZE, size_hint_y=None, height=30, background_color=WHITE, foreground_color=DARK_BLUE, size_hint_x=None, width=200))

        main_layout.add_widget(top_layout)

        # Lower half section - Two columns
        lower_half_layout = GridLayout(cols=2, size_hint_y=None, spacing=20, padding=10)

        # Left column
        left_column = GridLayout(cols=1, size_hint_y=None, spacing=20, padding=10)

        # Inspiration and Proficiency Bonus
        left_column.add_widget(Label(text="Inspiration", font_size=FONT_SIZE, color=DARK_BLUE))
        left_column.add_widget(TextInput(font_size=FONT_SIZE, multiline=False, background_color=WHITE, foreground_color=DARK_BLUE, size_hint_x=None, width=200))
        left_column.add_widget(Label(text="Proficiency Bonus", font_size=FONT_SIZE, color=DARK_BLUE))
        left_column.add_widget(TextInput(font_size=FONT_SIZE, multiline=False, background_color=WHITE, foreground_color=DARK_BLUE, size_hint_x=None, width=200))

        attributes = {
            "Strength": ["Saving Throw", "Athletics"],
            "Dexterity": ["Saving Throw", "Acrobatics", "Sleight of Hand", "Stealth"],
            "Constitution": ["Saving Throw", "Hit Points", "Death Saves"],
            "Intelligence": ["Saving Throw", "Arcana", "History", "Investigation", "Nature", "Religion"],
            "Wisdom": ["Saving Throw", "Animal Handling", "Insight", "Medicine", "Perception", "Survival"],
            "Charisma": ["Saving Throw", "Deception", "Intimidation", "Performance", "Persuasion"]
        }

        for attr, skills in attributes.items():
            attr_box = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=5)
            attr_box.add_widget(Label(text=attr, font_size=FONT_SIZE, color=DARK_BLUE))
            attr_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
            attr_row.add_widget(TextInput(font_size=FONT_SIZE, multiline=False, background_color=WHITE, foreground_color=DARK_BLUE, size_hint_x=None, width=50))
            attr_row.add_widget(TextInput(font_size=FONT_SIZE, multiline=False, background_color=WHITE, foreground_color=DARK_BLUE, size_hint_x=None, width=50))
            attr_box.add_widget(attr_row)

            for skill in skills:
                skill_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
                skill_row.add_widget(Label(text=skill, font_size=FONT_SIZE, color=DARK_BLUE, size_hint_x=None, width=200))
                skill_row.add_widget(TextInput(font_size=FONT_SIZE, multiline=False, background_color=WHITE, foreground_color=DARK_BLUE, size_hint_x=None, width=50))
                attr_box.add_widget(skill_row)

            left_column.add_widget(attr_box)

        lower_half_layout.add_widget(left_column)

        # Right column
        right_column = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=10)

        # Attacks section
        right_column.add_widget(Label(text="Attacks", font_size=FONT_SIZE, color=DARK_BLUE))
        attacks_layout = GridLayout(cols=3, size_hint_y=None, height=90, spacing=10)
        for i in range(3):
            attacks_layout.add_widget(TextInput(font_size=FONT_SIZE, multiline=False, background_color=WHITE, foreground_color=DARK_BLUE))  # Weapon Name
            attacks_layout.add_widget(TextInput(font_size=FONT_SIZE, multiline=False, background_color=WHITE, foreground_color=DARK_BLUE))  # Attack Bonus
            attacks_layout.add_widget(TextInput(font_size=FONT_SIZE, multiline=False, background_color=WHITE, foreground_color=DARK_BLUE))  # Damage/Type
        right_column.add_widget(attacks_layout)

        # Features and Traits section
        right_column.add_widget(Label(text="Features and Traits", font_size=FONT_SIZE, color=DARK_BLUE))
        right_column.add_widget(TextInput(font_size=FONT_SIZE, multiline=True, background_color=WHITE, foreground_color=DARK_BLUE, size_hint_y=None, height=100))

        # Reputations section
        right_column.add_widget(Label(text="Reputations", font_size=FONT_SIZE, color=DARK_BLUE))
        reputations_layout = GridLayout(cols=2, size_hint_y=None, height=90, spacing=10)
        for i in range(3):
            reputations_layout.add_widget(TextInput(font_size=FONT_SIZE, multiline=False, background_color=WHITE, foreground_color=DARK_BLUE))  # Organization
            reputations_layout.add_widget(TextInput(font_size=FONT_SIZE, multiline=False, background_color=WHITE, foreground_color=DARK_BLUE))  # Value
        right_column.add_widget(reputations_layout)

        # Equipment section
        right_column.add_widget(Label(text="Equipment", font_size=FONT_SIZE, color=DARK_BLUE))
        equipment_layout = GridLayout(cols=2, size_hint_y=None, height=180, spacing=10)
        for i in range(6):
            equipment_layout.add_widget(TextInput(font_size=FONT_SIZE, multiline=False, background_color=WHITE, foreground_color=DARK_BLUE))  # Item
            equipment_layout.add_widget(TextInput(font_size=FONT_SIZE, multiline=False, background_color=WHITE, foreground_color=DARK_BLUE))  # Weight
        right_column.add_widget(equipment_layout)

        # Encumbrance section
        right_column.add_widget(Label(text="Encumbrance", font_size=FONT_SIZE, color=DARK_BLUE))
        right_column.add_widget(TextInput(font_size=FONT_SIZE, multiline=False, background_color=WHITE, foreground_color=DARK_BLUE, size_hint_x=None, width=200))

        lower_half_layout.add_widget(right_column)

        main_layout.add_widget(lower_half_layout)

        scroll_view.add_widget(main_layout)
        self.add_widget(scroll_view)

        # OK button to save the data
        ok_button = Button(text="OK", size_hint_y=None, height=50, background_color=GREY, color=DARK_BLUE)
        ok_button.bind(on_release=self.save_character)
        self.add_widget(ok_button)

    def update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def save_character(self, instance):
        character_name = self.character_data['name']
        realm = self.realm_input.text
        if not realm:
            realm = "tier_1"
        filename = f"./saves/{character_name}.{realm}.json"
        with open(filename, 'w') as f:
            json.dump(self.character_data, f)
        popup = Popup(title='Saved', content=Label(text=f"Character saved as {filename}"), size_hint=(0.75, 0.5))
        popup.open()

class CharacterSheetApp(App):
    def build(self):
        input_file = sys.argv[1]
        with open(input_file, 'r') as f:
            character_data = json.load(f)
        return CharacterSheet(character_data)

if __name__ == "__main__":
    CharacterSheetApp().run()
