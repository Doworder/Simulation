from abc import ABC
from dataclasses import dataclass


class Entity(ABC):
    pass


class Grass(Entity):
    pass


class Rock(Entity):
    pass


class Tree(Entity):
    pass


class Creature(Entity):
    pass


class Herbivore(Creature):
    pass


class Predator(Creature):
    pass


@dataclass
class Coordinates:
    x: int
    y: int


class Map:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.entities = {}

    def get_entity(self, coordinates: Coordinates) -> Entity:
        return self.entities[coordinates]

    def add_entity(self, coordinates: Coordinates, entity: Entity) -> None:
        self.entities[coordinates] = entity

    def remove_entity(self, coordinates: Coordinates):
        if coordinates in self.entities:
            del self.entities[coordinates]


class Simulation:
    """Главный класс приложения, включает в себя:

        Карту
        Счётчик ходов
        Рендерер поля
        Actions - список действий, исполняемых перед
        стартом симуляции или на каждом ходу"""

    def __init__(self, width: int, height: int):
        self.map = Map(width, height)
        self._counter = 0

    def next_turn(self):
        """ росимулировать и отрендерить один ход"""

    def start_simulation(self):
        """- запустить бесконечный цикл симуляции и рендеринга"""

    def pause_simulation(self):
        """ - приостановить бесконечный цикл симуляции и рендеринга"""

