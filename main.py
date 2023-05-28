import sys
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow

from map import Map
from ship import Ship, WrongShipPlacementException
from window import Ui_MainWindow, WarshipsGraphicsView


def calculate_shadow(n):  # вычисляем вектор корабля, чтобы центр был нулем
    min = list(range(0, -1 * n // 2, -1))
    max = list(range(1, n // 2 + 1))
    min.sort()
    return tuple(min + max)


def shift_over_size(t: list[tuple[int, int]], field_size, direction: bool):
    q = any(map(lambda b: any(map(lambda i: i>=field_size, b)), t))  # проверка не вылазит ли тень за максимальный размер поля
    while q:  # сдвигаем в сторону центра, пока не будет влазить
        m = []
        for a in t:
            if direction:
                m.append((a[0]-1, a[1]))  # сдвиг по горизонтали
            else:
                m.append((a[0], a[1]-1))  # сдвиг по вертикали
        t = m
        q = any(map(lambda b: any(map(lambda i: i>=field_size, b)), t))  # перепроверяем
    q = any(map(lambda b: any(map(lambda i: i<0, b)), t))  # проверка не вылазит ли тень за ноль
    while q:
        m = []
        for a in t:
            if direction:
                m.append((a[0]+1, a[1]))  # сдвиг по горизонтали от нуля
            else:
                m.append((a[0], a[1]+1))  # сдвиг по вертикали от нуля
        t = m
        q = any(map(lambda b: any(map(lambda i: i<0, b)), t))  # перепроверяем
    return t  # возвращаем исправленную тень


def calculate_ship_coords(  # функция выдает координаты тени для отрисовки корабля
        size: int,
        center: tuple[int, int],
        direction: bool,
        field_size,
):
    ship_vector = calculate_shadow(size)  # получаем вектор тени
    retval = []
    for shadow_part in ship_vector:
        if direction:
            retval.append((center[0] + shadow_part, center[1]))  # размещаем тень горизонтально
        else:
            retval.append((center[0], center[1] + shadow_part))  # вертикально
    retval = shift_over_size(retval, field_size, direction)  # сдвигаем, чтоб не вылазила за край
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
    ui_window: Ui_MainWindow  # графическое окно
    ui_app: QApplication  # графическое приложение

    ship_placement_template = {  # список видов кораблей и их кол-во
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
        self.ui_window.setupUi(self.window)  # настраиваем графику (поля и тп)
        self.active_player = Player(  # создание игроков
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
        self.start_placing_ships()  # начинаем этап размещения кораблей

    def start_placing_ships(self):
        if self.active_player.unplaced_ships is None:  # в случае если игрок до этого не размещал корабли, то даем ему разместить
            self.active_player.unplaced_ships = self.ship_placement_template.copy()  # создаем инвентарь кораблей игроку
            self.ui_window.drawShipsInventory(self.active_player.unplaced_ships, self.pick_ship)  # рисуем инвентарь
            self.ui_window.drawShips(self.active_player.ships, self.active_player.field)  # красим поле активного игрока синим цветом
            return
        self.start_new_turn()  # если игрок уже размещал корабли, то начинаем игру

    def pick_ship(self, ship_size, icon, *args, **kwargs):  # вытаскиваем корабль из инвентаря
        self.current_ship_size = ship_size  # записываем размер корабля, который размещаем
        self.shadow_center = None  # обнуляем центр тени
        self.current_ship_direction = 0  # обнуляем направление корабля
        self.placement_icon = icon  # запоминаем иконку, которую нужно будет удалить из инвентаря
        for row in self.active_player.field:
            for cell in row:
                cell.setMouseTracking(True)  # включаем трансляцию событий при движении мыши
                cell.function_on_hover = self.ship_placement_on_hover  # записываем полям игрока функции для размещения
                cell.alternative_function = self.rotate_ship
                cell.instrument_function = self.place_ship_on_field
                cell.setForegroundBrush(QBrush(Qt.transparent))  # закрашиваем прозрачным цветом передний фон клеток

    def rotate_ship(self, *args, **kwargs):
        shadow_coords = calculate_ship_coords(  # вычисляем предыдущие координаты тени
            self.current_ship_size,
            self.shadow_center,
            bool(self.current_ship_direction),
            len(self.active_player.field),
        )
        for cell in shadow_coords:
            self.active_player.field[cell[0]][cell[1]].setForegroundBrush(QBrush(Qt.transparent))  # стираем тень

        self.current_ship_direction = abs(self.current_ship_direction - 1)  # меняем направление на противоположное для поворота корабля

        shadow_coords = calculate_ship_coords(  # рисуем новую тень
            self.current_ship_size,
            self.shadow_center,
            bool(self.current_ship_direction),
            len(self.active_player.field),
        )
        for cell in shadow_coords:
            self.active_player.field[cell[0]][cell[1]].setForegroundBrush(QBrush(QColor('gray')))

    def place_ship_on_field(self, coordinates: tuple[int, int], *args, **kwargs):
        shadow_coords = calculate_ship_coords(  # вычисляем координаты где хотим разместить корабль
            self.current_ship_size,
            coordinates,
            bool(self.current_ship_direction),
            len(self.active_player.field),
        )
        try:
            ship = Ship(tuple(self.active_player.map.fields[x][y] for x, y in shadow_coords))  # пытаемся по этим координатам корабль разместить
        except WrongShipPlacementException:
            return  # если не получилось, не делаем ничего

        self.active_player.ships.append(ship)  # добавляем корабль игроку
        self.active_player.unplaced_ships[self.current_ship_size] -= 1  # вычитаем корабль из инвентаря
        # возвращаем в исходное состояние клетки поля
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
        # до сих
        self.ui_window.drawShips(self.active_player.ships, self.active_player.field)  # рисуем корабли
        self.ui_window.horizontalLayout_2.removeWidget(self.placement_icon)  # убираем иконки из инвентаря
        self.placement_icon = None
        if all(unplaced_ship == 0 for unplaced_ship in self.active_player.unplaced_ships.values()):  # в случае если корабли закончились, то включаем паузу
            for i in self.inactive_player.field:
                for cell in i:
                    cell.instrument_function = partial(self.pause_game, next_action=self.start_placing_ships)
            for i in self.active_player.field:
                for cell in i:
                    cell.instrument_function = partial(self.pause_game, next_action=self.start_placing_ships)
            self.ui_window.centralwidget.instrument_function = partial(self.pause_game, next_action=self.start_placing_ships)
            self.active_player, self.inactive_player = self.inactive_player, self.active_player  # меняем игроков местами

    def ship_placement_on_hover(self, coordinates: tuple[int, int], *args, **kwargs):
        if self.shadow_center is None:
            self.shadow_center = coordinates  # записываем первые координаты
        # стираем старую тень
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
        # рисуем новую тень
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
                cell.instrument_function = self.make_turn  # записываем в клетки противника функцию для выстрела
        for i in self.active_player.field:
            for cell in i:
                cell.instrument_function = None  # убираем функцию стрельбы из своего поля
        self.ui_window.centralwidget.instrument_function = None  # убираем паузу
        self.ui_window.drawShips(self.active_player.ships, self.active_player.field)  # рисуем свои корабли
        self.ui_window.drawIntell(self.active_player.intell, self.inactive_player.field)  # рисуем разведку

    def pause_game(self, next_action, *args, **kwargs):  # функция очищает все поля и вешает ожидание следующего действия
        # ожидание
        for i in self.inactive_player.field:
            for cell in i:
                cell.instrument_function = next_action
        self.ui_window.centralwidget.instrument_function = next_action
        for i in self.active_player.field:
            for cell in i:
                cell.instrument_function = next_action
        # закрашивает белым
        self.ui_window.cleanField(self.active_player.field)
        self.ui_window.cleanField(self.inactive_player.field)

    def make_turn(self, coordinates, parent, event, *args, **kwargs):
        attacked_cell = self.inactive_player.map.fields[coordinates[0]][coordinates[1]]  # по координатам находим атакованную клетку
        self.active_player.intell.append(
            attacked_cell,  # открываем текущему игроку клетку
        )
        if attacked_cell.entity is not None:  # проверка наличия корабля в клетке
            attacked_entity = attacked_cell.entity  # запоминаем корабль
            if attacked_cell not in attacked_entity.damaged_cells:  # проверка, не попали ли мы второй раз по одной клетке
                attacked_entity.damaged_cells.append(attacked_cell)  # записываем клетку в поврежденные у корабля
                if len(attacked_entity.damaged_cells) == len(attacked_entity.position_cells):  # если целых клеток больше нет
                    attacked_entity.destroyed = True  # помечаем корабль как уничтоженный
                    self.active_player.intell.extend(attacked_entity.around_cells)  # показываем окружающие клетки
                    if all(ship.destroyed for ship in self.inactive_player.ships):  # если все корабли уничтожены
                        self.finish_game()  # рисуем окно победителя
                        return
                self.ui_window.drawIntell(self.active_player.intell, self.inactive_player.field)  # отрисовываем полученную информацию
            return  # возвращаем ход игроку обратно
        self.ui_window.drawIntell(self.active_player.intell, self.inactive_player.field)  # отрисовываем полученную информацию
        # ставим на паузу игру
        for i in self.inactive_player.field:
            for cell in i:
                cell.instrument_function = partial(self.pause_game, next_action=self.start_new_turn)
        for i in self.inactive_player.field:
            for cell in i:
                cell.instrument_function = partial(self.pause_game, next_action=self.start_new_turn)
        self.ui_window.centralwidget.instrument_function = partial(self.pause_game, next_action=self.start_new_turn)
        # меняем игроков местами
        self.active_player, self.inactive_player = self.inactive_player, self.active_player

    def finish_game(self):
        self.ui_window.finish(self.active_player, self.start_new_game)  # отрисовываем окно победителя


if __name__ == '__main__':
    game = Game()  # создаем игру
    game.ui_app.exec_()  # запуск графического приложения
