import sys
import json
import glob
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsItem
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtCore import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QPushButton  # Add this import

def load_equipment(filename='saves/loot.json'):
    with open(filename, 'r') as file:
        return json.load(file)

class InventoryItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, item_type):
        super().__init__(pixmap)
        self.item_type = item_type
        self.initial_position = QPointF()  # Placeholder for the initial position
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptDrops(True)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            slots = [item for item in self.scene().items() if isinstance(item, PaperdollSlot)]
            empty_slot_exists = any(slot.slot_type == self.item_type and not slot.has_item for slot in slots)
            if empty_slot_exists:
                self.initial_position = self.pos()  
                super().mousePressEvent(event)
            else:
                print(f"No empty slot available for item type: {self.item_type}")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            slots = [item for item in self.scene().items() if isinstance(item, PaperdollSlot)]
            for slot in slots:
                if slot.slot_type == self.item_type and not slot.has_item and self.is_within_slot(slot):
                    self.setPos(slot.pos())
                    slot.has_item = True
                    super().mouseReleaseEvent(event)
                    return
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            new_pos = value
            return self.snap_to_grid(new_pos)
        return super().itemChange(change, value)

    def snap_to_grid(self, pos):
        grid_size = 50
        x = round(pos.x() / grid_size) * grid_size
        y = round(pos.y() / grid_size) * grid_size
        return QPointF(x, y)

    def is_within_slot(self, slot):
        item_rect = QRectF(self.pos(), QSizeF(self.pixmap().size()))
        slot_rect = QRectF(slot.pos(), QSizeF(slot.rect().width(), slot.rect().height()))
        return slot_rect.contains(item_rect.center())

class PaperdollSlot(QGraphicsRectItem):
    def __init__(self, x, y, width, height, slot_type):
        super().__init__(x, y, width, height)
        self.slot_type = slot_type
        self.has_item = False
        self.setPen(Qt.GlobalColor.blue)
        self.setBrush(Qt.GlobalColor.lightGray)
        self.setAcceptDrops(True)

    def get_slot_info(self):
        if self.has_item:
            item = self.scene().itemAt(self.pos(), QTransform())  # Get the item in the slot
            if isinstance(item, InventoryItem):
                return {
                    "slot_type": self.slot_type,
                    "item_type": item.item_type,
                    "item_name": item.data(0)  # Assuming you store item name in item's data
                }
        return {"slot_type": self.slot_type, "item_type": None, "item_name": None}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory GUI with Paperdoll")
        self.setGeometry(100, 100, 800, 600)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.create_paperdoll()
        self.create_inventory()
        self.save_button = QPushButton("Save Inventory", self)
        self.save_button.setGeometry(650, 500, 120, 40)  # Example position and size
        self.save_button.clicked.connect(self.save_inventory)

    def create_paperdoll(self):
        slots = [
            {'x': 300, 'y': 50, 'width': 50, 'height': 50, 'type': 'head'},
            {'x': 300, 'y': 150, 'width': 50, 'height': 50, 'type': 'body'},
            {'x': 250, 'y': 150, 'width': 50, 'height': 50, 'type': 'left_hand'},
            {'x': 350, 'y': 150, 'width': 50, 'height': 50, 'type': 'right_hand'}
        ]
        for slot in slots:
            slot_item = PaperdollSlot(slot['x'], slot['y'], slot['width'], slot['height'], slot['type'])
            self.scene.addItem(slot_item)

    def create_inventory(self):
        items = load_equipment()
        for item in items:
            image_path = f'images/{item["image"]}'  # Correct path to the image files
            item_pixmap = QPixmap(image_path)
            if item_pixmap.isNull():
                print(f"Failed to load image: {image_path}")
                continue
            inventory_item = InventoryItem(item_pixmap, item['type'])
            inventory_item.setPos(50, 50 * items.index(item) + 50)
            self.scene.addItem(inventory_item)

    def save_inventory(self):
        slots = [item for item in self.scene.items() if isinstance(item, PaperdollSlot)]
        slot_data = [slot.get_slot_info() for slot in slots]

        # Find the most recently updated character in /saves
        save_files = glob.glob('saves/*.json')
        latest_file = max(save_files, key=os.path.getmtime)
        character_name = os.path.splitext(os.path.basename(latest_file))[0]

        # Save the slot data to a JSON file named after the character
        filename = f'saves/inv/{character_name}.inv.json'
        with open(filename, 'w') as f:
            json.dump(slot_data, f, indent=4)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
