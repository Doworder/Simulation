from simulation.coordinates import Point
from simulation.entities import Entity
from simulation.world_map import Map


class Renderer:
    """Выполняет отрисовки в консоли"""
    PREVIEW = """
        Welcome to the 2D world simulation. 
        Use the keyboard to interact with the program.
        Press (S, Enter) to start or (N, Enter) to one circle or (E, Enter) to exit"""
    STARTED = """
        Press (P, Enter) to pause or (E, Enter) to exit"""
    PAUSED = """
        Press (S, Enter) to start or (N, Enter) to one circle or (E, Enter) to exit"""
    NEXT = """
        Press (S, Enter) to start or (N, Enter) to one circle or (E, Enter) to exit"""

    def __init__(self, world_map: Map, rendering_symbols: dict[type[Entity], str], default_symbol: str):
        self.default_symbol = default_symbol
        self._map = world_map
        self._rendering_symbols = rendering_symbols

    def _render(self):
        width = self._map.width
        height = self._map.height

        for j in range(height):
            for i in range(width):
                coord = Point(i, j)
                if coord not in self._map.get_used_points():
                    print(self.default_symbol, end='')
                else:
                    entity = self._map.get_entity(coord)
                    print(self._rendering_symbols.get(type(entity)), end='')
            print()

    def preview(self):
        self._render()
        print(self.PREVIEW)

    def started(self):
        self._render()
        print(self.STARTED)

    def paused(self):
        self._render()
        print(self.PAUSED)

    def nexted(self):
        self._render()
        print(self.NEXT)
