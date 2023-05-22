import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QGraphicsGridLayout, QLabel, QGraphicsItem, \
    QPushButton, \
    QWidget, QGridLayout, QGraphicsView, QAction, QStatusBar, QMenuBar, QHBoxLayout, QGraphicsScene
from PyQt5.QtCore import Qt, QRect, QCoreApplication, QMetaObject
from PyQt5.QtGui import QPixmap, QColor, QPainter, QMouseEvent, QBrush
from PyQt5 import QtGui

from map import Map

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
SQUARE_SIDE = 20
ROWS, COLS = int(WINDOW_HEIGHT/SQUARE_SIDE), int(WINDOW_WIDTH/2*SQUARE_SIDE)

class WarshipsGraphicsView(QGraphicsView):

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        print('t')
        t = self.backgroundBrush()
        print(t.color().getRgb())


class Ui_MainWindow(object):
    def setupUi(self, MainWindow, field_size: int = 10):
        size = int(min(WINDOW_WIDTH * 0.45, WINDOW_HEIGHT * 0.8))
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(20, 10, 761, 341))
        self.horizontalLayoutWidget = QWidget(self.widget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(0, 0, 761, 341))
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
                graphicsView = WarshipsGraphicsView(self.graphics_scene, self.widget)
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
                graphicsView = WarshipsGraphicsView(self.graphics_scene, self.widget)
                graphicsView.setFixedSize(int(size / field_size), int(size / field_size))
                self.gridLayout_2.addWidget(graphicsView, i, y, 1, 1)
                self.gridCells[i].append(graphicsView)

        self.horizontalLayout.addLayout(self.gridLayout_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def DrawWarshipsFields(self, current_player_map: Map, other_player_map: Map):
        for row in current_player_map.fields:
            for cell in row:
                visual_object: WarshipsGraphicsView = self.gridCells[cell.coordinates[0]][cell.coordinates[1]]
                if cell.entity is not None:
                    visual_object.setBackgroundBrush(QBrush(QColor(100, 100, 100)))

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
    # retranslateUi

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui_windoes = Ui_MainWindow()
    ui_windoes.setupUi(window)
    window.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.setWindowTitle("Warships")
    window.show()
    app.exec_()
