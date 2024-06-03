#paperdoll.py
import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsItem
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QPointF

def load_equipment(filename='saves/loot.json'):
    with open(filename, 'r') as file:
        return json.load(file)

class InventoryItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, item_type):
        super().__init__(pixmap)
        self.item_type = item_type
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptDrops(True)

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

class PaperdollSlot(QGraphicsRectItem):
    def __init__(self, x, y, width, height, slot_type):
        super().__init__(x, y, width, height)
        self.slot_type = slot_type
        self.setPen(Qt.GlobalColor.blue)
        self.setBrush(Qt.GlobalColor.lightGray)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if isinstance(event.source(), InventoryItem) and event.source().item_type == self.slot_type:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        item = event.source()
        if item.item_type == self.slot_type:
            item.setPos(self.pos())
            event.acceptProposedAction()
        else:
            event.ignore()

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

    def create_paperdoll(self):
        slots = [
            {'x': 300, 'y': 50, 'width': 50, 'height': 50, 'type': 'head'},
            {'x': 300, 'y': 150, 'width': 50, 'height': 50, 'type': 'body'},
            {'x': 250, 'y': 150, 'width': 50, 'height': 50, 'type': 'left_hand'},
            {'x': 350, 'y': 150, 'width': 50, 'height': 50, 'type': 'right_hand'}
        ]
        for slot in slots:
            self.scene.addItem(PaperdollSlot(slot['x'], slot['y'], slot['width'], slot['height'], slot['type']))

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
