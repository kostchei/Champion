#kivy version
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

class CharacterSheet(BoxLayout):
    def __init__(self, character_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Scrollable content
        scroll_view = ScrollView()
        grid_layout = GridLayout(cols=2, size_hint_y=None)
        grid_layout.bind(minimum_height=grid_layout.setter('height'))

        # Character details and attributes
        details = {
            "Character Name": character_data['name'],
            "Gender": character_data['gender'],
            "Game Edition": character_data['game_edition'],
            "Race": character_data['race'],
            "Class": character_data['class'],
            "Background": character_data['background']
        }

        for label, value in details.items():
            grid_layout.add_widget(Label(text=f"{label}:", font_size='20sp', size_hint_y=None, height=40))
            grid_layout.add_widget(Label(text=str(value), font_size='20sp', size_hint_y=None, height=40))

        attributes = {
            "Strength": character_data['strength'],
            "Dexterity": character_data['dexterity'],
            "Constitution": character_data['constitution'],
            "Intelligence": character_data['intelligence'],
            "Wisdom": character_data['wisdom'],
            "Charisma": character_data['charisma']
        }

        for label, value in attributes.items():
            grid_layout.add_widget(Label(text=f"{label}:", font_size='20sp', size_hint_y=None, height=40))
            grid_layout.add_widget(Label(text=str(value), font_size='20sp', size_hint_y=None, height=40))

        # Placeholder for other attributes
        other_attributes = [
            "Race", "Age", "Background", "XP",
            "Eyes", "Hair", "Height", "Weight",
            "Proficiency", "Inspiration", "Passive Perception"
        ]
        for attr in other_attributes:
            grid_layout.add_widget(Label(text=attr, font_size='20sp', size_hint_y=None, height=40))
            grid_layout.add_widget(TextInput(size_hint_y=None, height=40))

        skills = ["Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", "History"]
        for skill in skills:
            grid_layout.add_widget(Label(text=skill, font_size='20sp', size_hint_y=None, height=40))
            grid_layout.add_widget(TextInput(size_hint_y=None, height=40))

        # Realm selection
        grid_layout.add_widget(Label(text="Realm:", font_size='20sp', size_hint_y=None, height=40))
        self.realm_input = TextInput(text="tier_1", size_hint_y=None, height=40)
        grid_layout.add_widget(self.realm_input)

        scroll_view.add_widget(grid_layout)
        self.add_widget(scroll_view)

        # OK button to save the data
        ok_button = Button(text="OK", size_hint_y=None, height=50)
        ok_button.bind(on_release=lambda x: self.save_character(character_data))
        self.add_widget(ok_button)

    def save_character(self, character_data):
        character_name = character_data['name']
        realm = self.realm_input.text
        if not realm:
            realm = "tier_1"
        filename = f"./saves/{character_name}.{realm}.json"
        with open(filename, 'w') as f:
            json.dump(character_data, f)
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
