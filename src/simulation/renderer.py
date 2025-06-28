from os import system, name

from simulation.condition import Condition, Status
from simulation.coordinates import Point


class Renderer:
    """Выполняет отрисовки в консоли"""
    PREVIEW = """
        Welcome to the 2D world simulation. 
        Use the keyboard to interact with the program.
        Press (S, Enter) to start or (N, Enter) to one circle or (E, Enter) to exit"""
    START = """
        Press (P, Enter) to pause or (E, Enter) to exit"""
    STEP = """
        Press (S, Enter) to start or (N, Enter) to one circle or (E, Enter) to exit"""
    STOP = """
            Stop simulation.
            Quit"""

    def __init__(
            self,
            world_map: "Map",
            rendering_symbols: dict[type["Entity"], str],
            default_symbol: str,
            state: Condition
    ):
        self._state = state
        self.default_symbol = default_symbol
        self._map = world_map
        self._rendering_symbols = rendering_symbols

    def render(self, turn_counter: int):
        width = self._map.width
        height = self._map.height

        self.clear()

        for j in range(height):
            for i in range(width):
                coord = Point(i, j)
                if coord not in self._map.get_used_points():
                    print(self.default_symbol, end='')
                else:
                    entity = self._map.get_entity(coord)
                    print(self._rendering_symbols.get(type(entity)), end='')
            print()

        print(f'Turns completed: {turn_counter}')

        match self._state.status:
            case Status.START:
                self.started()

            case Status.PAUSE:
                self.paused()

            case Status.STEP:
                self.paused()

            case Status.STOP:
                self.stoped()

    def preview(self):
        self.render(0)
        print(self.PREVIEW)

    def started(self):
        print(self.START)

    def paused(self):
        print(self.STEP)

    def stoped(self):
        print(self.STOP)

    @staticmethod
    def clear():
        system('cls' if name == 'nt' else 'clear')
