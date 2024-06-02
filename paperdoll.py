#paperdoll.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsItem
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QPointF

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
        grid_size = 50  # Assuming each slot is 50x50
        x = round(pos.x() / grid_size) * grid_size
        y = round(pos.y() / grid_size) * grid_size
        return QPointF(x, y)  # Return the snapped position

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

    def dropEvent(self, event):
        item = event.source()
        item.setPos(self.pos())
        event.acceptProposedAction()

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
        item_pixmap = QPixmap(50, 50)
        item_pixmap.fill(Qt.GlobalColor.red)

        items = [
            {'type': 'head', 'pos': (50, 50)},
            {'type': 'body', 'pos': (50, 150)},
            {'type': 'left_hand', 'pos': (50, 250)},
            {'type': 'right_hand', 'pos': (50, 350)}
        ]

        for item in items:
            inventory_item = InventoryItem(item_pixmap, item['type'])
            inventory_item.setPos(*item['pos'])
            self.scene.addItem(inventory_item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

