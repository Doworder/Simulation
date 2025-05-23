from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import randint
from collections import deque


@dataclass(frozen=True)
class Coordinates:
    x: int
    y: int


class Entity(ABC):
    """Есть мысль хранить текущие координаты объекта в атрибуте объекта, обновлять их при перемещении,
       тогда не нужно будет их искать для текущего объекта(find_current_coord)"""
    pass


class Map:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.entities: dict = {}
        self.creatures: set = set()

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
    def __init__(self, speed: int, health: int):
        self.speed = speed
        self.hp = health

    @abstractmethod
    def make_move(self):
        pass

    def find_path_to_resource(self, map: Map, resource: Entity) -> list[Coordinates] | None:
        processed: list = []
        coord: Coordinates = self.find_current_coord(self, map)
        search_queue: deque[Coordinates] = deque()
        search_queue.append((coord, []))
        while search_queue:
            entity_coord, path_to_resource = search_queue.popleft()
            if entity_coord in processed:
                continue

            processed.append(entity_coord)

            if isinstance(map.entities.get(entity_coord), resource):
                return path_to_resource

            if isinstance(map.entities.get(entity_coord), Entity):
                if entity_coord is not coord:
                    continue

            neiborgs = self.get_neighbors(entity_coord, path_to_resource, map)
            search_queue += neiborgs

        return [coord]



    @staticmethod
    def find_current_coord(value, map: Map) -> Coordinates|None:
        """Возвращает значение координат объекта value из map"""
        for coord, entity in map.entities.items():
            if entity == value:
                return coord
        return None

    @staticmethod
    def get_neighbors(coords: Coordinates, path: list, map: Map) -> list:
        neighbors_coords = [
            (coords.x, coords.y+1),
            (coords.x+1, coords.y),
            (coords.x, coords.y-1),
            (coords.x-1, coords.y)
        ]
        return [(Coordinates(x, y), path + [coords]) for x, y in neighbors_coords if (0 <= x < map.width and 0 <= y < map.height)]


class Herbivore(Creature):
    def __init__(self, speed: int, health: int):
        super().__init__(speed, health)

    def make_move(self, map: Map):
        """Выполнить ход, либо съесть травы"""
        path: list = self.find_path_to_resource(map, Grass)
        if len(path) == 1:
            map.entities.pop(path[0])

        elif len(path) <= self.speed:
            current_entity = map.entities.pop(self.find_current_coord(self, map))
            map.entities[path[-2]] = current_entity

        else:
            current_entity = map.entities.pop(self.find_current_coord(self, map))
            map.entities[path[self.speed]] = current_entity

    def attacked(self, attack_power: int):
        self.hp -= attack_power


class Predator(Creature):
    def __init__(self, speed: int, health: int, attack_power: int):
        super().__init__(speed, health)
        self.ap = attack_power

    def make_move(self, map: Map):
        """Выполнить ход, атаковать"""
        path: list = self.find_path_to_resource(map, Herbivore)
        if len(path) <= self.speed:
            current_entity = map.entities.pop(self.find_current_coord(self, map))
            map.entities[path[-2]] = current_entity
            map.entities[path[-1]].attacked(self.ap)

        current_entity = map.entities.pop(self.find_current_coord(self, map))
        map.entities[path[self.speed]] = current_entity


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
            if isinstance(self.entity, Creature):
                map.creatures.add(self.entity)
            spawn_limit -= 1


class SpawnEntity(Actions):
    def do(self, entity) -> Entity:
        return entity


class MoveEntity(Actions):
    def do(self, map: Map) -> None:
        for entity in map.creatures:
            if isinstance(entity, Creature):
                entity.make_move(map)


class DelEntity(Actions):
    def do(self, entity):
        del entity


class FindDeadEntity(Actions):
    def is_dead(self, entity) -> bool:
        if entity.hp > 0:
            return False
        return True

    def do(self, map: Map):
        for entity in map.entities.values():
            if isinstance(entity, Creature):
                if self.is_dead(entity):
                    DelEntity.do(entity)


class Simulation:
    """Главный класс приложения, включает в себя:

        Карту
        Счётчик ходов
        Рендер поля
        Actions - список действий, исполняемых перед
        стартом симуляции или на каждом ходу"""

    init_actions: list = [
        InitAction(Grass()),
        InitAction(Rock()),
        InitAction(Tree()),
        InitAction(Herbivore(1, 5)),
        InitAction(Predator(2, 10, 3))
    ]
    turn_actions: list = [
        FindDeadEntity(),
        MoveEntity()
    ]

    def __init__(self, width: int, height: int):
        self.map = Map(width, height)
        self._counter = 0

    def next_turn(self):
        """ Просимулировать и отрендерить один ход"""
        for action in self.turn_actions:
            action.do(self.map)

        self.map_renderer()

    def start_simulation(self):
        """- запустить бесконечный цикл симуляции и рендеринга"""
        while True:
            self.next_turn()

    def pause_simulation(self):
        """ - приостановить бесконечный цикл симуляции и рендеринга"""
        input('Нажмите Enter для продолжения...')

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


if __name__ == '__main__':
    world = Simulation(10, 10)
    for action in world.init_actions:
        action.do(0.1, world.map)

    world.map_renderer()
    world.next_turn()

    # entities = [Grass, Rock, Tree, Herbivore, Predator]
    #
    # init_grass = InitAction(SpawnEntity().do(Grass()))
    # world.init_actions.append(init_grass)
    #
    # init_rock = InitAction(SpawnEntity().do(Rock()))
    # world.init_actions.append(init_rock)
    #
    # init_tree = InitAction(SpawnEntity().do(Tree()))
    # world.init_actions.append(init_tree)
    #
    # init_herbivore = InitAction(SpawnEntity().do(Herbivore(1, 10)))
    # world.init_actions.append(init_herbivore)
    #
    # init_predator = InitAction(SpawnEntity().do(Predator(3, 10, 5)))
    # world.init_actions.append(init_predator)
    #
    # # for init_action in world.init_actions:
    # #     init_action.do(0.1, world.map)
    #
    # world.map.add_entity(Coordinates(1,1), Herbivore(1, 10))
    # world.map.add_entity(Coordinates(5,5), Grass())
    # world.map.add_entity(Coordinates(1,4), Tree())
    # entity: Creature = world.map.entities[Coordinates(1, 1)]
    # path_to_res = entity.find_path_to_resource(world.map, Grass)
    # # pprint(path_to_res)
    # print(path_to_res)
    #
    # print(world.__dict__)
    # print(world.map.__dict__)
    # world.map_renderer()
