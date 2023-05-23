import asyncio
import sys
import time
from functools import partial

from PyQt5.QtWidgets import QApplication, QMainWindow

from map import Map
from ship import Ship
from window import Ui_MainWindow, WarshipsGraphicsView


class Player:
    name: str
    map: Map
    ships: list[Ship]
    intell: list[Map.MapCell]
    field: list[list[WarshipsGraphicsView]]

    def __init__(
        self,
        name,
        map,
        ships,
        intell,
        field,
    ):
        self.name = name
        self.map = map
        self.ships = list(ships)
        self.intell = list(intell)
        self.field = field


class Game:
    active_player: Player
    inactive_player: Player
    ui_window: Ui_MainWindow
    ui_app: QApplication

    def __init__(
        self,
    ):
        self.ui_window = Ui_MainWindow()
        self.ui_app = QApplication(sys.argv)
        window = QMainWindow()
        window.setFixedSize(800, 600)
        window.setWindowTitle("Warships")
        window.show()
        self.ui_window.setupUi(window)
        self.active_player = Player(
            name='Dodik',
            map=Map(size=10),
            ships=(),
            intell=(),
            field=self.ui_window.gridCells,
        )
        self.inactive_player = Player(
            name='Dodik2',
            map=Map(size=10),
            ships=(),
            intell=(),
            field=self.ui_window.gridCells_2,
        )
        self.place_ships()
        self.start_game()

    def place_ships(self):
        player1 = self.active_player
        player1.ships.append(Ship(
            (
                player1.map.fields[1][2],
                player1.map.fields[1][3],
                player1.map.fields[1][4],
            )
        ))
        player2 = self.inactive_player
        player2.ships.append(Ship(
            (
                player2.map.fields[2][1],
                player2.map.fields[3][1],
                player2.map.fields[4][1],
            )
        ))

    def start_game(self):
        self.ui_window.drawShips(self.active_player.ships)
        self.ui_window.drawIntell(self.active_player.intell)
        for i in self.inactive_player.field:
            for cell in i:
                cell.instrument_function = self.make_turn

    def make_turn(self, coordinates, parent, event, *args, **kwargs):
        print(coordinates)


if __name__ == '__main__':
    game = Game()
    game.ui_app.exec_()
