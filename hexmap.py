# hexmap.py
from collections import deque
import numpy as np
import hexy as hx
import pygame as pg
from PIL import Image, ImageDraw
import os
import random

TARGET_FPS = 60
HEX_RADIUS = 30
VIEWPORT_PIXEL_SIZE = (1600, 1600)
SOFT_BROWN_GREEN = (231, 247, 161) # forest or plains colour

# Define terrain types and their corresponding images
script_dir = os.path.dirname(os.path.abspath(__file__))
terrain_types = {
    "forest": os.path.join(script_dir, "images", "forest.png"),
    "open": os.path.join(script_dir, "images", "open.png"),
    "hill": os.path.join(script_dir, "images", "hill.png"),
    "water": os.path.join(script_dir, "images", "water.png"),
    "settlement": os.path.join(script_dir, "images", "settlement.png")
}

# Define the probabilities for each terrain type
terrain_probabilities = {
    "forest": 0.75,
    "hill": 0.10,
    "open": 0.10,
    "water": 0.03,
    "settlement": 0.02
}

def scale_image(image, hex_radius):
    # Calculate the new size preserving the aspect ratio
    original_size = image.size
    scale_ratio = (hex_radius * 1.9) / max(original_size)
    new_size = tuple([int(dim * scale_ratio) for dim in original_size])
    return image.resize(new_size, Image.Resampling.LANCZOS)

# Load and scale images
terrain_images = {}
for key, value in terrain_types.items():
    try:
        image = Image.open(value)
        terrain_images[key] = scale_image(image, HEX_RADIUS)
    except FileNotFoundError as e:
        print(f"Error loading image for terrain type '{key}': {value}")
        print(str(e))
        exit(1)

# Convert PIL images to Pygame surfaces
def pil_to_pygame(image):
    mode = image.mode
    size = image.size
    data = image.tobytes()
    return pg.image.fromstring(data, size, mode)

terrain_surfaces = {key: pil_to_pygame(image) for key, image in terrain_images.items()}

class ExampleHex(hx.HexTile):
    def __init__(self, axial_coordinates, terrain, radius):
        self.axial_coordinates = np.array([axial_coordinates])
        self.cube_coordinates = hx.axial_to_cube(self.axial_coordinates)
        self.position = hx.axial_to_pixel(self.axial_coordinates, radius)
        self.terrain = terrain
        self.radius = radius
        self.image = terrain_surfaces[terrain]
        self.value = None

    def set_value(self, value):
        self.value = value

    def get_draw_position(self):
        draw_position = self.position[0] - [self.image.get_width() / 2, self.image.get_height() / 2]
        return draw_position

    def get_position(self):
        return self.position[0]

class ExampleHexMap:
    def __init__(self, viewport_pixel_size=VIEWPORT_PIXEL_SIZE, hex_radius=HEX_RADIUS, caption="ExampleHexMap"):
        self.viewport_pixel_size = viewport_pixel_size
        self.caption = caption

        self.size = np.array(viewport_pixel_size)
        self.width, self.height = self.size
        self.center = self.size / 2

        self.hex_radius = hex_radius

        self.hex_map = hx.HexMap()
        self.max_coord = 8

        self.selection_radius = ClampedInteger(3, 1, 5)

        self.selected_hex_image = make_hex_surface(
            (128, 128, 128, 180),
            self.hex_radius,
            (255, 255, 255),
            hollow=False,
            border=5)

        self.selection_type = CyclicInteger(3, 0, 4)
        self._clicked_hex_as_cube_coord = np.array([[0, 0, 0]])

        all_coordinates = hx.get_disk(np.array((0, 0, 0)), self.max_coord)
        col_idx = np.random.randint(0, 4, len(all_coordinates))

        hexes = []
        num_shown_hexes = np.random.binomial(len(all_coordinates), .95)
        axial_coordinates = hx.cube_to_axial(all_coordinates)
        axial_coordinates = axial_coordinates[np.random.choice(len(axial_coordinates), num_shown_hexes, replace=False)]

        terrain_choices = list(terrain_probabilities.keys())
        terrain_weights = list(terrain_probabilities.values())

        for i, axial in enumerate(axial_coordinates):
            terrain = random.choices(terrain_choices, weights=terrain_weights, k=1)[0]
            hexes.append(ExampleHex(axial, terrain, hex_radius))
            hexes[-1].set_value(i)

        self.hex_map[np.array(axial_coordinates)] = hexes

        self.main_surf = None
        self.font = None
        self.clock = None
        self.init_pg()

    @property
    def clicked_hex_as_cube_coord(self):
        return self._clicked_hex_as_cube_coord[0]

    @property
    def clicked_hex_axial_coord(self):
        return hx.cube_to_axial(self._clicked_hex_as_cube_coord)

    def init_pg(self):
        pg.init()
        self.main_surf = pg.display.set_mode(self.viewport_pixel_size)
        pg.display.set_caption(self.caption)

        pg.font.init()
        self.font = pg.font.SysFont("monospace", 14, True)
        self.clock = pg.time.Clock()

    def handle_events(self):
        running = True
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._clicked_hex_as_cube_coord = hx.pixel_to_cube(
                        np.array([pg.mouse.get_pos() - self.center]),
                        self.hex_radius)
                if event.button == 3:
                    self.selection_type += 1
                if event.button == 4:
                    self.selection_radius += 1
                if event.button == 5:
                    self.selection_radius -= 1

            if event.type == pg.KEYUP:
                if event.key == pg.K_UP:
                    self.selection_radius += 1
                elif event.key == pg.K_DOWN:
                    self.selection_radius -= 1

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False

        return running

    def main_loop(self):
        running = self.handle_events()
        return running

    def draw(self):
        hexagons = list(self.hex_map.values())
        self.main_surf.blits((hexagon.image, hexagon.get_draw_position() + self.center) for hexagon in hexagons)

        for hexagon in list(self.hex_map.values()):
            # Comment out or remove the lines below to stop displaying numbers
            # text = self.font.render(str(hexagon.value), False, (0, 0, 0))
            # text.set_alpha(160)
            # text_pos = hexagon.get_position() + self.center
            # text_pos -= (text.get_width() / 2, text.get_height() / 2)
             # self.main_surf.blit(text, text_pos)

            mouse_pos = np.array([pg.mouse.get_pos()]) - self.center
            mouse_pos_as_cube_coord = hx.pixel_to_cube(mouse_pos, self.hex_radius)[0]
            selected_hexes_cube_coords = Selection.get_selection(self.selection_type.value, mouse_pos_as_cube_coord,
                                                             self.selection_radius, self.clicked_hex_as_cube_coord)

        selected_hexes_axial_coords = hx.cube_to_axial(selected_hexes_cube_coords)
        selected_hexes = self.hex_map[selected_hexes_axial_coords]
        deque(map(self.draw_selected_hex, selected_hexes), maxlen=0)

        self.draw_HUD(mouse_pos, selected_hexes_cube_coords)
        pg.display.update()
        self.main_surf.fill((SOFT_BROWN_GREEN))
        self.clock.tick(TARGET_FPS)

    def draw_HUD(self, mouse_pos, selected_hexes_cube_coords):
        selection_type_text = self.font.render(
            "(Right Click To Change) Selection Type: " + Selection.Type.to_string(self.selection_type.value),
            True, (50, 50, 50))
        radius_text = self.font.render(
            "(Scroll Mouse Wheel To Change) Radius: " + str(self.selection_radius.value),
            True, (50, 50, 50))
        fps_text = self.font.render(" FPS: " + str(int(self.clock.get_fps())), True, (50, 50, 50))
        clicked_hx_coord = self.font.render(" clicked hex coord (cubic): " + str(self._clicked_hex_as_cube_coord),
                                            True, (50, 50, 50))
        clicked_hexes = self.hex_map[self.clicked_hex_axial_coord]
        clicked_hx_text = self.font.render(" clicked hex: " + str(clicked_hexes[0]) if clicked_hexes else "_", True,
                                           (50, 50, 50))
        mouse_pos_text = self.font.render(f" mouse pos : {pg.mouse.get_pos()} => {mouse_pos} ", True,
                                          (50, 50, 50))
        rad_hex_text = self.font.render(f"rad_hex selection {selected_hexes_cube_coords}", True, (50, 50, 50))

        display_driver_text = self.font.render(f"PG display driver: {pg.display.get_driver()}", True,  (50,50,50))
        self.main_surf.blit(fps_text, (5, 0))
        self.main_surf.blit(radius_text, (5, 15))
        self.main_surf.blit(selection_type_text, (5, 30))
        self.main_surf.blit(clicked_hx_coord, (5, 45))
        self.main_surf.blit(clicked_hx_text, (5, 60))
        self.main_surf.blit(mouse_pos_text, (self.viewport_pixel_size[0] - mouse_pos_text.get_width(), 0))
        self.main_surf.blit(display_driver_text, (self.viewport_pixel_size[0] - display_driver_text.get_width(), 15))
        self.main_surf.blit(rad_hex_text, (5, 75))

    def draw_selected_hex(self, hexagon):
        self.main_surf.blit(self.selected_hex_image, hexagon.get_draw_position() + self.center)

    def quit_app(self):
        pg.quit()
        raise SystemExit


class ClampedInteger:
    def __init__(self, initial_value, lower_limit, upper_limit):
        self.value = initial_value
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def __iadd__(self, other):
        self.value = min(self.value + other, self.upper_limit)
        return self

    def __isub__(self, other):
        self.value = max(self.value - self.lower_limit, self.lower_limit)
        return self


class CyclicInteger:
    def __init__(self, initial_value, lower_limit, upper_limit):
        self.value = initial_value
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def __iadd__(self, other):
        self.value += other
        if self.value > self.upper_limit:
            self.value = self.lower_limit
        return self

    def __isub__(self, other):
        self.value -= other
        if self.value < self.lower_limit:
            self.value = self.upper_limit
        return self


class Selection:
    class Type:
        POINT = 0
        RING = 1
        DISK = 2
        LINE = 3
        SPIRAL = 4

        @staticmethod
        def to_string(selection_type):
            if selection_type == Selection.Type.DISK:
                return "disk"
            elif selection_type == Selection.Type.RING:
                return "ring"
            elif selection_type == Selection.Type.LINE:
                return "line"
            elif selection_type == Selection.Type.SPIRAL:
                return "spiral"
            else:
                return "point"

    @staticmethod
    def get_selection(selection_type, cube_mouse, selection_radius, clicked_hex=None):
        if selection_type == Selection.Type.DISK:
            return hx.get_disk(cube_mouse, selection_radius.value)
        elif selection_type == Selection.Type.RING:
            return hx.get_ring(cube_mouse, selection_radius.value)
        elif selection_type == Selection.Type.LINE:
            return hx.get_hex_line(clicked_hex, cube_mouse)
        elif selection_type == Selection.Type.SPIRAL:
            click_rad = int(hx.get_cube_distance([0, 0, 0], clicked_hex))
            mouse_rad = int(hx.get_cube_distance([0, 0, 0], cube_mouse))
            return hx.get_spiral([0, 0, 0], min(click_rad, mouse_rad), max(click_rad, mouse_rad))
        else:
            return np.array([cube_mouse.copy()])

def make_hex_surface(color, radius, border_color=(100, 100, 100), border=True, hollow=False):
    angles_in_radians = np.deg2rad([60 * i + 30 for i in range(6)])
    x = radius * np.cos(angles_in_radians)
    y = radius * np.sin(angles_in_radians)
    points = np.round(np.vstack([x, y]).T)

    sorted_x = sorted(points[:, 0])
    sorted_y = sorted(points[:, 1])
    minx = sorted_x[0]
    maxx = sorted_x[-1]
    miny = sorted_y[0]
    maxy = sorted_y[-1]

    sorted_idxs = np.lexsort((points[:, 0], points[:, 1]))

    surf_size = np.array((maxx - minx, maxy - miny)) * 2 + 1
    center = surf_size / 2
    surface = pg.Surface(surf_size)
    surface.set_colorkey((0, 0, 0))

    if len(color) >= 4:
        surface.set_alpha(color[-1])

    if not hollow:
        pg.draw.polygon(surface, color, points + center, 0)

    points[sorted_idxs[-1:-4:-1]] += [0, 1]
    if border or hollow:
        pg.draw.lines(surface, border_color, True, points + center, 1)

    return surface
