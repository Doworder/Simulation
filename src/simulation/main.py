from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import randint
from collections import deque


@dataclass(frozen=True)
class Coordinates:
    x: int
    y: int


class Entity(ABC):
    pass


class Map:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.entities: dict = {}

    def get_entity(self, coordinates: Coordinates) -> Entity:
        return self.entities[coordinates]

    def add_entity(self, coordinates: Coordinates, entity: Entity) -> None:
        self.entities[coordinates] = entity

    def remove_entity(self, coordinates: Coordinates):
        if coordinates in self.entities:
            del self.entities[coordinates]


class Grass(Entity):
    pass


class Rock(Entity):
    pass


class Tree(Entity):
    pass


class Creature(Entity):
    speed: int = 0
    hp: int = 0

    @abstractmethod
    def make_move(self):
        pass

    def find_resource(self, map: Map, resource: Entity) -> Coordinates|None:
        processed: list = []
        coord: Coordinates = self.find_current_coord(self, map)
        graph: dict[Coordinates, list[Coordinates]] = {}
        search_queue: deque[Coordinates] = deque()
        search_queue.append(coord)
        while search_queue:
            entity_coord = search_queue.popleft()
            if entity_coord in processed:
                continue

            processed.append(entity_coord)

            if map.entities.get(entity_coord) == resource:
                return entity_coord

            neiborgs = self.get_neighbors(entity_coord)
            search_queue += neiborgs
            graph[entity_coord] = neiborgs

        return None



    @staticmethod
    def find_current_coord(value, map: Map):
        """Возвращает значение координат объекта value из map"""
        for coord, entity in map.entities:
            if entity == value:
                return coord
            return "There is no such Coordinates"

    @staticmethod
    def get_neighbors(coords: Coordinates) -> list:
        return [Coordinates(coords.x, coords.y+1),
                Coordinates(coords.x+1, coords.y),
                Coordinates(coords.x, coords.y-1),
                Coordinates(coords.x-1, coords.y)]


class Herbivore(Creature):
    def __init__(self, speed: int, health: int):
        self.speed = speed
        self.hp = health

    def make_move(self):
        """Выполнить ход, либо съесть травы"""


class Predator(Creature):
    def __init__(self, speed: int, health: int, attack_power: int):
        self.speed = speed
        self.hp = health
        self.ap = attack_power

    def make_move(self):
        """Выполнить ход, атаковать"""


class Simulation:
    """Главный класс приложения, включает в себя:

        Карту
        Счётчик ходов
        Рендер поля
        Actions - список действий, исполняемых перед
        стартом симуляции или на каждом ходу"""

    init_actions: list = []
    turn_actions: list = []

    def __init__(self, width: int, height: int):
        self.map = Map(width, height)
        self._counter = 0

    def next_turn(self):
        """ Просимулировать и отрендерить один ход"""

    def start_simulation(self):
        """- запустить бесконечный цикл симуляции и рендеринга"""

    def pause_simulation(self):
        """ - приостановить бесконечный цикл симуляции и рендеринга"""

    def map_renderer(self):
        width = self.map.width
        height = self.map.height
        rendering_symbols = {
            Predator: 'P ',
            Herbivore: 'H ',
            Grass: 'G ',
            Rock: 'R ',
            Tree: 'T '
        }

        for i in range(height):
            for j in range(width):
                coord = Coordinates(i, j)
                if coord not in self.map.entities:
                    print('* ', end='')
                else:
                    print(rendering_symbols[(self.map.entities[coord]).__class__], end='')
            print()


class Actions(ABC):
    @abstractmethod
    def do(self) -> None:
        pass


class InitAction(Actions):
    def __init__(self, entity: Entity):
        self.entity = entity

    def do(self, spawn_coef: float, map: Map) -> None:
        spawn_limit: int = int(map.width * map.height * spawn_coef)
        while spawn_limit:
            coordinate = Coordinates(randint(0, map.width - 1), randint(0, map.height - 1))
            if coordinate in map.entities:
                continue
            map.add_entity(coordinate, self.entity)
            spawn_limit -= 1


class SpawnEntity(Actions):
    def do(self, entity) -> Entity:
        return entity


if __name__ == '__main__':
    world = Simulation(10, 10)
    entities = [Grass, Rock, Tree, Herbivore, Predator]

    init_grass = InitAction(SpawnEntity().do(Grass()))
    world.init_actions.append(init_grass)

    init_rock = InitAction(SpawnEntity().do(Rock()))
    world.init_actions.append(init_rock)

    init_tree = InitAction(SpawnEntity().do(Tree()))
    world.init_actions.append(init_tree)

    init_herbivore = InitAction(SpawnEntity().do(Herbivore(1, 10)))
    world.init_actions.append(init_herbivore)

    init_predator = InitAction(SpawnEntity().do(Predator(3, 10, 5)))
    world.init_actions.append(init_predator)

    for init_action in world.init_actions:
        init_action.do(0.1, world.map)

    # def init_entities_on_map(entities: list, world: Simulation) -> None:
    #     for entity in entities:
    #         for _ in range(10):
    #             coordinate = Coordinates(randint(0, 9), randint(0, 9))
    #             if coordinate in world.map.entities:
    #                 continue
    #             world.map.add_entity(coordinate, entity)
    #
    # init_entities_on_map(entities, world)

    print(world.__dict__)
    print(world.map.__dict__)
    world.map_renderer()
