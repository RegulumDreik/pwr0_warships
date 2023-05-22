from ship import Ship


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
