# main.py
from hexmap import ExampleHexMap

if __name__ == '__main__':
    example_hex_map = ExampleHexMap()

    while example_hex_map.main_loop():
        example_hex_map.draw()

    example_hex_map.quit_app()
