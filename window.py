import sys
from typing import Collection, Callable, Optional

from PyQt5.QtWidgets import QApplication, QMainWindow,  QLabel, \
    QWidget, QGridLayout, QGraphicsView, QHBoxLayout, QGraphicsScene, QBoxLayout
from PyQt5.QtCore import Qt, QRect, QCoreApplication, QMetaObject
from PyQt5.QtGui import QPixmap, QColor, QPainter, QMouseEvent, QBrush, QPen, QFont
from PyQt5 import QtGui

from map import Map
from ship import Ship

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
SQUARE_SIDE = 20
ROWS, COLS = int(WINDOW_HEIGHT/SQUARE_SIDE), int(WINDOW_WIDTH/2*SQUARE_SIDE)

class WarshipsGraphicsView(QGraphicsView):

    coordinates: tuple[int, int]
    instrument_function: Optional[Callable]  # LMB
    alternative_function: Optional[Callable]  # RMB
    function_on_hover: Optional[Callable]

    def __init__(self, coordinates, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instrument_function = None
        self.alternative_function = None
        self.function_on_hover = None
        self.coordinates = coordinates

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            if self.instrument_function is not None:
                self.instrument_function(coordinates=self.coordinates, parent=self.parent(), event=event)
        else:
            if self.alternative_function is not None:
                self.alternative_function(coordinates=self.coordinates, parent=self.parent(), event=event)


    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.function_on_hover is not None:
            self.function_on_hover(self.coordinates, self.underMouse())


class InstrumentedWidget(QWidget):

    instrument_function: Optional[Callable]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instrument_function = None

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.instrument_function is not None:
            self.instrument_function()


class IconWidget(InstrumentedWidget):
    def __init__(self, ship_size: int, scene, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.ship_size = ship_size

        layout = QHBoxLayout()
        self.setLayout(layout)

        icon_pixmap = self.generate_icon_pixmap(40, 100, QColor('gray'), ship_size, 20)

        item = scene.addPixmap(icon_pixmap)
        item.setFlag(item.ItemIsMovable)

        label = QLabel()
        label.setPixmap(icon_pixmap)
        layout.addWidget(label)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.instrument_function is not None:
            self.instrument_function(self.ship_size, self)

    @staticmethod
    def generate_icon_pixmap(width, height, color, ship_size, max_width):
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setBrush(color)
        block_height = min((height // ship_size), max_width)
        position = ((width - block_height) // 2)
        for i in range(ship_size):
            painter.drawRect(position, i*block_height, block_height, block_height)
        painter.end()

        return pixmap


class Ui_MainWindow(object):
    def setupUi(self, MainWindow, field_size: int = 10):
        size = int(min(WINDOW_WIDTH * 0.45, WINDOW_HEIGHT * 0.8))
        self.main_window = MainWindow
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.centralwidget = InstrumentedWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(20, 10, 760, 340))
        self.horizontalLayoutWidget = QWidget(self.widget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(0, 0, 760, 340))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.graphics_scene = QGraphicsScene(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSpacing(0)
        self.gridCells = []
        for i in range(field_size):
            self.gridCells.append([])
            for y in range(field_size):
                graphicsView = WarshipsGraphicsView((i, y), self.graphics_scene, self.widget, )
                graphicsView.setFixedSize(int(size / field_size), int(size / field_size))
                self.gridLayout.addWidget(graphicsView, i, y, 1, 1)
                self.gridCells[i].append(graphicsView)

        self.horizontalLayout.addLayout(self.gridLayout)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")

        self.gridLayout_2.setSpacing(0)
        self.gridCells_2 = []
        for i in range(field_size):
            self.gridCells_2.append([])
            for y in range(field_size):
                graphicsView = WarshipsGraphicsView((i, y), self.graphics_scene, self.widget)
                graphicsView.setFixedSize(int(size / field_size), int(size / field_size))
                self.gridLayout_2.addWidget(graphicsView, i, y, 1, 1)
                self.gridCells_2[i].append(graphicsView)

        self.horizontalLayout.addLayout(self.gridLayout_2)

        self.horizontalLayoutWidget_2 = QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setObjectName(u"horizontalLayoutWidget_2")
        self.horizontalLayoutWidget_2.setGeometry(QRect(20, 360, 750, 200))
        self.graphics_scene_2 = QGraphicsScene(self.widget)
        self.horizontalLayout_2 = QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setDirection(QBoxLayout.Direction.LeftToRight)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)  # I dunno what it doing.
    # setupUi

    def cleanField(self, target_field=None):
        if target_field is None:
            target_field = self.gridCells
        for row in target_field:
            for cell in row:
                cell.setBackgroundBrush(QBrush(QColor(255, 255, 255)))

    def drawShips(self, ships: Collection[Ship], target_field=None):
        if target_field is None:
            target_field = self.gridCells
        for row in target_field:
            for cell in row:
                cell.setBackgroundBrush(QBrush(QColor(167, 195, 217)))
        for ship in ships:
            for cell in ship.position_cells:
                visual_object: WarshipsGraphicsView = target_field[cell.coordinates[0]][cell.coordinates[1]]
                if ship.destroyed:
                    visual_object.setBackgroundBrush(QBrush(QColor(173, 37, 3)))
                    continue
                if cell in ship.damaged_cells:
                    visual_object.setBackgroundBrush(QBrush(QColor(255, 174, 66)))
                    continue
                visual_object.setBackgroundBrush(QBrush(QColor(100, 100, 100)))

    def drawIntell(self, intell: Collection[Map.MapCell], target_field=None):
        if target_field is None:
            target_field = self.gridCells_2
        for spy in intell:
            visual_object: WarshipsGraphicsView = target_field[spy.coordinates[0]][spy.coordinates[1]]
            if spy.entity is None:
                visual_object.setBackgroundBrush(QBrush(QColor(167, 195, 217)))
                continue
            if spy.entity.destroyed:
                visual_object.setBackgroundBrush(QBrush(QColor(173, 37, 3)))
                continue
            if spy in spy.entity.damaged_cells:
                visual_object.setBackgroundBrush(QBrush(QColor(255, 174, 66)))
                continue

    def drawShipsInventory(self, ship_inventory: dict[int, int], instument_function = None):
        for key, value in ship_inventory.items():
            for _ in range(value):
                icon = IconWidget(key, self.graphics_scene_2, self.widget)
                icon.instrument_function = instument_function
                self.horizontalLayout_2.addWidget(icon, alignment=Qt.AlignCenter)

    def finish(self, player, next_game_function = None):
        finish_widget = InstrumentedWidget(self.main_window)
        layout = QHBoxLayout(finish_widget)
        win_label = QLabel(f'{player.name} WINNER', finish_widget)
        win_label.setFont(QFont("Arial", 40, QFont.Bold))
        layout.addWidget(win_label, alignment=Qt.AlignCenter)
        finish_widget.setLayout(layout)
        finish_widget.instrument_function = next_game_function
        self.main_window.setCentralWidget(finish_widget)


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
    # retranslateUi
