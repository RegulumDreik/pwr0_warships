from typing import Any, Collection


class WrongShipPlacementException(Exception):
    pass


class Ship:
    name: str
    position_cells: list['MapCell']
    around_cells: list['MapCell']


class ShipAround:
    pass





class Map:
    fields: list[list['Map.MapCell']]
    size: int

    class MapCell:
        entity: Ship
        around_entities: list[Ship]
        parent_map: 'Map'
        coordinates: tuple[int, int]

        def __init__(self, map: 'Map', coordinates: tuple[int, int], ship: Ship = None):
            self.entity = ship
            self.around_entities = []
            self.parent_map = map
            self.coordinates = coordinates


    def __init__(self, size: int = 10):
        self.fields = []
        self.size = size
        for x in range(self.size):
            tmp = []
            for y in range(self.size):
                tmp.append(Map.MapCell(self, (x, y)))
            self.fields.append(tmp)


class Player:
    name: str
    map: Map


def add_ship(
    cells: Collection[Map.MapCell]
) -> Ship:
    current_ship = Ship()
    current_ship.position_cells = cells
    current_ship.around_cells = []

    if not all(cell.entity is None for cell in cells):
        raise WrongShipPlacementException('Ship is cannot be putted here.')

    for cell in cells:
        cell.entity = current_ship
    for cell in cells:
        coord_x, coord_y = cell.coordinates
        for map_x in range(
                max(coord_x-1, 0),
                min(coord_x+1, cell.parent_map.size) + 1
        ):
            for map_y in range(
                    max(coord_y-1, 0),
                    min(coord_y+1, cell.parent_map.size) + 1
            ):
                current_cell = cell.parent_map.fields[map_x][map_y]
                if current_ship not in current_cell.around_entities:
                    current_cell.around_entities.append(current_ship)
                if current_cell not in current_ship.around_cells:
                    current_ship.around_cells.append(current_cell)

    return current_ship

if __name__ == '__main__':
    map = Map(size=10)
    t = add_ship((map.fields[1][1], map.fields[1][2], map.fields[1][3]))
    try:
        t = add_ship((map.fields[1][3], map.fields[1][4], map.fields[1][5]))
    except WrongShipPlacementException:
        print('Ship is cannot be putted here.')
    print('t')
