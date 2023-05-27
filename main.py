import asyncio
import sys
import time
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow

from map import Map
from ship import Ship, WrongShipPlacementException, WrongShipFormException
from window import Ui_MainWindow, WarshipsGraphicsView

def calculate_shadow(n):
    min = list(range(0, -1 * n // 2, -1))
    max = list(range(1, n // 2 + 1))
    min.sort()
    return tuple(min + max)



def shift_over_size(t: list[tuple[int, int]], field_size, direction: bool):
    q = any(map(lambda b: any(map(lambda i: i>=field_size, b)), t))
    while q:
        m = []
        for a in t:
            if direction:
                m.append((a[0]-1, a[1]))
            else:
                m.append((a[0], a[1]-1))
        t = m
        q = any(map(lambda b: any(map(lambda i: i>=field_size, b)), t))
    q = any(map(lambda b: any(map(lambda i: i<0, b)), t))
    while q:
        m = []
        for a in t:
            if direction:
                m.append((a[0]+1, a[1]))
            else:
                m.append((a[0], a[1]+1))
        t = m
        q = any(map(lambda b: any(map(lambda i: i<0, b)), t))
    return t

def calculate_ship_coords(
        size: int,
        center: tuple[int, int],
        direction: bool,
        field_size,
):
    ship_vector = calculate_shadow(size)
    retval = []
    for shadow_part in ship_vector:
        if direction:
            retval.append((center[0] + shadow_part, center[1]))
        else:
            retval.append((center[0], center[1] + shadow_part))
    retval = shift_over_size(retval, field_size, direction)
    return retval




class Player:
    name: str
    map: Map
    ships: list[Ship]
    intell: list[Map.MapCell]
    field: list[list[WarshipsGraphicsView]]
    unplaced_ships: dict[int, int] = None

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

    ship_placement_template = {
        4: 1,
        3: 2,
        2: 3,
        1: 4,
    }
    shadow_center = None
    current_ship_size = None
    current_ship_direction = 0
    placement_icon = None

    def __init__(
        self,
    ):
        self.ui_window = Ui_MainWindow()
        self.ui_app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setFixedSize(800, 600)
        self.window.setWindowTitle("Warships")
        self.window.show()
        self.start_new_game()

    def start_new_game(self, *args, **kwargs):
        self.ui_window.setupUi(self.window)
        self.active_player = Player(
            name='p1',
            map=Map(size=10),
            ships=(),
            intell=(),
            field=self.ui_window.gridCells,
        )
        self.inactive_player = Player(
            name='p2',
            map=Map(size=10),
            ships=(),
            intell=(),
            field=self.ui_window.gridCells_2,
        )
        self.start_placing_ships()

    def start_placing_ships(self):
        if self.active_player.unplaced_ships is None:
            self.active_player.unplaced_ships = self.ship_placement_template.copy()
            self.ui_window.drawShipsInventory(self.active_player.unplaced_ships, self.pick_ship)
            self.ui_window.drawShips(self.active_player.ships, self.active_player.field)
            return
        self.start_new_turn()

    def pick_ship(self, ship_size, icon, *args, **kwargs):
        self.current_ship_size = ship_size
        self.shadow_center = None
        self.current_ship_direction = 0
        self.placement_icon = icon
        for row in self.active_player.field:
            for cell in row:
                cell.setMouseTracking(True)
                cell.function_on_hover = self.ship_placement_on_hover
                cell.alternative_function = self.rotate_ship
                cell.instrument_function = self.place_ship_on_field
                cell.setForegroundBrush(QBrush(Qt.transparent))

    def rotate_ship(self, *args, **kwargs):
        shadow_coords = calculate_ship_coords(
            self.current_ship_size,
            self.shadow_center,
            bool(self.current_ship_direction),
            len(self.active_player.field),
        )
        for cell in shadow_coords:
            self.active_player.field[cell[0]][cell[1]].setForegroundBrush(QBrush(Qt.transparent))

        self.current_ship_direction = abs(self.current_ship_direction - 1)

        shadow_coords = calculate_ship_coords(
            self.current_ship_size,
            self.shadow_center,
            bool(self.current_ship_direction),
            len(self.active_player.field),
        )
        for cell in shadow_coords:
            self.active_player.field[cell[0]][cell[1]].setForegroundBrush(QBrush(QColor('gray')))

    def place_ship_on_field(self, coordinates: tuple[int, int], *args, **kwargs):
        shadow_coords = calculate_ship_coords(
            self.current_ship_size,
            coordinates,
            bool(self.current_ship_direction),
            len(self.active_player.field),
        )
        try:
            ship = Ship(tuple(self.active_player.map.fields[x][y] for x, y in shadow_coords))
        except WrongShipPlacementException:
            return

        self.active_player.ships.append(ship)
        self.active_player.unplaced_ships[self.current_ship_size] -= 1
        self.current_ship_size = None
        self.shadow_center = None
        self.current_ship_direction = 0
        for row in self.active_player.field:
            for cell in row:
                cell.setMouseTracking(False)
                cell.function_on_hover = None
                cell.instrument_function = None
                cell.alternative_function = None
                cell.setForegroundBrush(QBrush(Qt.transparent))
        self.ui_window.drawShips(self.active_player.ships, self.active_player.field)
        self.ui_window.horizontalLayout_2.removeWidget(self.placement_icon)
        self.placement_icon = None
        if all(unplaced_ship == 0 for unplaced_ship in self.active_player.unplaced_ships.values()):
            for i in self.inactive_player.field:
                for cell in i:
                    cell.instrument_function = partial(self.pause_game, next_action=self.start_placing_ships)
            for i in self.active_player.field:
                for cell in i:
                    cell.instrument_function = partial(self.pause_game, next_action=self.start_placing_ships)
            self.ui_window.centralwidget.instrument_function = partial(self.pause_game, next_action=self.start_placing_ships)
            self.active_player, self.inactive_player = self.inactive_player, self.active_player

    def ship_placement_on_hover(self, coordinates: tuple[int, int], *args, **kwargs):
        if self.shadow_center is None:
            self.shadow_center = coordinates
        if coordinates != self.shadow_center:
            shadow_coords = calculate_ship_coords(
                self.current_ship_size,
                self.shadow_center,
                bool(self.current_ship_direction),
                len(self.active_player.field),
            )
            for cell in shadow_coords:
                self.active_player.field[cell[0]][cell[1]].setForegroundBrush(QBrush(Qt.transparent))
            self.shadow_center = coordinates
        shadow_coords = calculate_ship_coords(
            self.current_ship_size,
            self.shadow_center,
            bool(self.current_ship_direction),
            len(self.active_player.field),
        )
        for cell in shadow_coords:
            self.active_player.field[cell[0]][cell[1]].setForegroundBrush(QBrush(QColor('gray')))

    def start_new_turn(self, *args, **kwargs):
        for i in self.inactive_player.field:
            for cell in i:
                cell.instrument_function = self.make_turn
        for i in self.active_player.field:
            for cell in i:
                cell.instrument_function = None
        self.ui_window.centralwidget.instrument_function = None
        self.ui_window.drawShips(self.active_player.ships, self.active_player.field)
        self.ui_window.drawIntell(self.active_player.intell, self.inactive_player.field)

    def pause_game(self, next_action, *args, **kwargs):
        for i in self.inactive_player.field:
            for cell in i:
                cell.instrument_function = next_action
        self.ui_window.centralwidget.instrument_function = next_action
        for i in self.active_player.field:
            for cell in i:
                cell.instrument_function = next_action
        self.ui_window.cleanField(self.active_player.field)
        self.ui_window.cleanField(self.inactive_player.field)

    def make_turn(self, coordinates, parent, event, *args, **kwargs):
        attacked_cell = self.inactive_player.map.fields[coordinates[0]][coordinates[1]]
        self.active_player.intell.append(
            attacked_cell,
        )
        if attacked_cell.entity is not None:
            attacked_entity = attacked_cell.entity
            if attacked_cell not in attacked_entity.damaged_cells:
                attacked_entity.damaged_cells.append(attacked_cell)
                if len(attacked_entity.damaged_cells) == len(attacked_entity.position_cells):
                    attacked_entity.destroyed = True
                    self.active_player.intell.extend(attacked_entity.around_cells)
                    if all(ship.destroyed for ship in self.inactive_player.ships):
                        self.finish_game()
                        return
                self.ui_window.drawIntell(self.active_player.intell, self.inactive_player.field)
            return
        self.ui_window.drawIntell(self.active_player.intell, self.inactive_player.field)
        for i in self.inactive_player.field:
            for cell in i:
                cell.instrument_function = partial(self.pause_game, next_action=self.start_new_turn)
        for i in self.inactive_player.field:
            for cell in i:
                cell.instrument_function = partial(self.pause_game, next_action=self.start_new_turn)
        self.ui_window.centralwidget.instrument_function = partial(self.pause_game, next_action=self.start_new_turn)
        self.active_player, self.inactive_player = self.inactive_player, self.active_player

    def finish_game(self):
        self.ui_window.finish(self.active_player, self.start_new_game)

if __name__ == '__main__':
    game = Game()
    game.ui_app.exec_()
