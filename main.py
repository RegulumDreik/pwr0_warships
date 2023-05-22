import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from map import Map
from ship import Ship
from window import Ui_MainWindow


class Player:
    name: str
    map: Map
    ships: list[Ship]


if __name__ == '__main__':
    map = Map(size=10)
    Ship((map.fields[1][1], map.fields[1][2], map.fields[1][3]))
    Ship((map.fields[5][4], map.fields[6][4], map.fields[7][4], map.fields[8][4]))

    app = QApplication(sys.argv)
    window = QMainWindow()
    ui_windoes = Ui_MainWindow()
    ui_windoes.setupUi(window)
    window.setFixedSize(800, 600)
    window.setWindowTitle("Warships")
    window.show()
    ui_windoes.DrawWarshipsFields(map, map)
    app.exec_()

