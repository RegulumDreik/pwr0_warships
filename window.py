import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QGraphicsGridLayout, QLabel, QGraphicsItem, \
    QPushButton, \
    QWidget, QGridLayout, QGraphicsView, QAction
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QColor, QPainter, QMouseEvent
from PyQt5 import QtGui

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
SQUARE_SIDE = 20
ROWS, COLS = int(WINDOW_HEIGHT/SQUARE_SIDE), int(WINDOW_WIDTH/2*SQUARE_SIDE)

def clicked(*args, **kwargs):
    print('t')

class WarshipsGraphicsView(QGraphicsView):

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        print('t')

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent) -> None:
        print('t')

class MainWindow(QMainWindow):

    def __init__(self, field_size: int = 10):
        super().__init__()
        widget = QWidget()
        gridLayoutWidget = QWidget(widget)
        size = int(min(WINDOW_WIDTH*0.45, WINDOW_HEIGHT*0.8))
        gridLayoutWidget.setFixedSize(size, size)
        gridLayout = QGridLayout(gridLayoutWidget)
        gridLayout.setSpacing(0)
        for i in range(field_size):
            for y in range(field_size):
                graphicsView = WarshipsGraphicsView(gridLayoutWidget)
                graphicsView.setFixedSize(int(size/field_size), int(size/field_size))
                gridLayout.addWidget(graphicsView, i, y, 1, 1)
        self.setCentralWidget(widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(10)
    window.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.setWindowTitle("Warships")
    window.show()
    app.exec_()