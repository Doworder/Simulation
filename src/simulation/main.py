from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import randint


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


@dataclass(frozen=True)
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

    def map_renderer(self):
        width = self.map.width
        height = self.map.height
        rendering_symbols = {
            Predator: 'P',
            Herbivore: 'H',
            Grass: 'G',
            Rock: 'R',
            Tree: 'T'
        }

        for i in range(height):
            for j in range(width):
                coord = Coordinates(i, j)
                if coord not in self.map.entities:
                    print('*', end='')
                else:
                    print(rendering_symbols[self.map.entities[coord]], end='')
            print()


class Actions(ABC):
    @abstractmethod
    def do(self) -> None:
        pass


if __name__ == '__main__':
    world = Simulation(10, 10)
    for entity in [Grass, Rock, Tree, Herbivore, Predator]:
        for i in range(10):
            coord = Coordinates(randint(0, 9), randint(0, 9))
            if coord in world.map.entities:
                continue
            world.map.add_entity(coord, entity)

    print(world.__dict__)
    print(world.map.__dict__)
    world.map_renderer()
