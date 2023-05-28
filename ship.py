from typing import Collection


class WrongShipPlacementException(Exception):
    pass


class WrongShipFormException(Exception):
    pass


class Ship:
    name: str
    position_cells: list['MapCell']
    around_cells: list['MapCell']
    damaged_cells: list['MapCell']
    destroyed: bool = False

    def __init__(
        self,
        cells: Collection['Map.MapCell']
    ):
        self.position_cells = list(cells)
        self.around_cells = []
        self.damaged_cells = []

        if not check_chain_cell(cells):
            raise WrongShipFormException('Ship has wrong form.')

        if not all(len(cell.around_entities) == 0 for cell in cells):  # ошибка, при попытке поставить корабли рядом друг с другом
            raise WrongShipPlacementException('Ship is cannot be putted here.')

        for cell in cells:
            cell.entity = self
        for cell in cells:
            coord_x, coord_y = cell.coordinates
            for map_x in range(
                    max(coord_x - 1, 0),
                    min(coord_x + 1, cell.parent_map.size - 1) + 1
            ):
                for map_y in range(
                        max(coord_y - 1, 0),
                        min(coord_y + 1, cell.parent_map.size - 1) + 1
                ):
                    current_cell = cell.parent_map.fields[map_x][map_y]
                    if self not in current_cell.around_entities:  # добавление информации об окружающих корабль клетках
                        current_cell.around_entities.append(self)
                    if current_cell not in self.around_cells:
                        self.around_cells.append(current_cell)


def check_chain_cell(cells: Collection['Map.MapCell']) -> bool:  # проверка на целостность корабля - что он прямой и последовательный
    prev_x = None
    prev_y = None
    for cell in cells:
        coord_x, coord_y = cell.coordinates
        if prev_x is not None and abs(prev_x - coord_x) > 1:
            return False
        if prev_y is not None and abs(prev_y - coord_y) > 1:
            return False
        prev_x = coord_x
        prev_y = coord_y
    allcoord_x = [cell.coordinates[0] for cell in cells]
    allcoord_y = [cell.coordinates[1] for cell in cells]
    if not (all(coord_x == allcoord_x[0] for coord_x in allcoord_x) or all(coord_y == allcoord_y[0] for coord_y in allcoord_y)):
        return False
    return True
