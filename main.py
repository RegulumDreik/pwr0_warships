import asyncio
import sys
import time
from functools import partial

from PyQt5.QtCore import QTimer
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
    unplaced_ships: dict[int, int]

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

    def start_new_turn(self, *args, **kwargs):
        for i in self.inactive_player.field:
            for cell in i:
                cell.instrument_function = self.make_turn
        for i in self.active_player.field:
            for cell in i:
                cell.instrument_function = None
        self.ui_window.drawShips(self.active_player.ships, self.active_player.field)
        self.ui_window.drawIntell(self.active_player.intell, self.inactive_player.field)

    def pause_game(self, *args, **kwargs):
        for i in self.inactive_player.field:
            for cell in i:
                cell.instrument_function = self.start_new_turn
        self.ui_window.cleanField(self.active_player.field)
        self.ui_window.cleanField(self.inactive_player.field)
        self.ui_window.centralwidget.instrument_function = self.start_new_turn
        for i in self.active_player.field:
            for cell in i:
                cell.instrument_function = self.start_new_turn

    def make_turn(self, coordinates, parent, event, *args, **kwargs):
        attacked_cell = self.inactive_player.map.fields[coordinates[0]][coordinates[1]]
        self.active_player.intell.append(
            attacked_cell,
        )
        if attacked_cell.entity is not None:
            attacked_entity = attacked_cell.entity
            if attacked_cell not in attacked_entity.damaged_cells:
                attacked_entity.damaged_cells.append(attacked_cell)
                print('damaged')
            if len(attacked_entity.damaged_cells) == len(attacked_entity.position_cells):
                attacked_entity.destroyed = True
                self.active_player.intell.extend(attacked_entity.around_cells)
                print('destroyed')

        self.ui_window.drawIntell(self.active_player.intell, self.inactive_player.field)
        for i in self.inactive_player.field:
            for cell in i:
                cell.instrument_function = self.pause_game
        for i in self.inactive_player.field:
            for cell in i:
                cell.instrument_function = self.pause_game
        self.ui_window.centralwidget.instrument_function = self.pause_game
        self.active_player, self.inactive_player = self.inactive_player, self.active_player


if __name__ == '__main__':
    game = Game()
    game.ui_app.exec_()
