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
                path_to_resource.append(entity_coord)
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
            map.entities[path[self.speed - 1]] = current_entity

    def attacked(self, attack_power: int):
        self.hp -= attack_power


class Predator(Creature):
    def __init__(self, speed: int, health: int, attack_power: int):
        super().__init__(speed, health)
        self.ap = attack_power

    def make_move(self, map: Map):
        """Выполнить ход, атаковать"""
        path: list = self.find_path_to_resource(map, Herbivore)
        if len(path) == 1:
            map.entities.pop(path[0])

        elif len(path) <= self.speed:
            current_entity = map.entities.pop(self.find_current_coord(self, map))
            map.entities[path[-2]] = current_entity
            map.entities[path[-1]].attacked(self.ap)

        else:
            current_entity = map.entities.pop(self.find_current_coord(self, map))
            map.entities[path[self.speed - 1]] = current_entity


class Actions(ABC):
    @abstractmethod
    def do(self) -> None:
        pass


class InitAction(Actions):
    def __init__(self, spawn_coef: float, map: Map, entity: Entity):
        self.entity = entity
        self.spawn_coef = spawn_coef
        self.map = map

    def do(self) -> None:
        spawn_limit: int = int(self.map.width * self.map.height * self.spawn_coef)
        while spawn_limit:
            coordinate = Coordinates(randint(0, self.map.width - 1), randint(0, self.map.height - 1))
            if coordinate in self.map.entities:
                continue
            if self.entity is Rock:
                self.map.add_entity(coordinate, SpawnRock.do())

            elif self.entity is Tree:
                self.map.add_entity(coordinate, SpawnTree.do())

            elif self.entity is Grass:
                self.map.add_entity(coordinate, SpawnGrass.do())

            elif self.entity is Herbivore:
                herbivore = SpawnHerbivore.do()
                self.map.add_entity(coordinate, herbivore)
                self.map.creatures.add(herbivore)

            elif self.entity is Predator:
                predator = SpawnPredator.do()
                self.map.add_entity(coordinate, predator)
                self.map.creatures.add(predator)

            spawn_limit -= 1


class SpawnRock(Actions):
    @classmethod
    def do(cls) -> Rock:
        return Rock()


class SpawnTree(Actions):
    @classmethod
    def do(cls) -> Tree:
        return Tree()


class SpawnGrass(Actions):
    @classmethod
    def do(cls) -> Grass:
        return Grass()


class SpawnHerbivore(Actions):
    @classmethod
    def do(cls) -> Herbivore:
        return Herbivore(1, 10)


class SpawnPredator(Actions):
    @classmethod
    def do(cls) -> Predator:
        return Predator(3,10, 3)


class MoveEntity(Actions):
    def __init__(self, map: Map):
        self.map = map

    def do(self) -> None:
        for entity in self.map.creatures:
            if isinstance(entity, Creature):
                entity.make_move(self.map)


class DelEntity(Actions):
    def __init__(self, entity: Entity):
        self.entity = entity

    def do(self):
        del self.entity


class FindDeadEntity(Actions):
    def __init__(self, map: Map):
        self.map = map

    def is_dead(self, entity) -> bool:
        if entity.hp > 0:
            return False
        return True

    def do(self):
        for entity in self.map.creatures:
            if self.is_dead(entity):
                self.map.creatures.discard(entity)
                del self.map.entities[entity.find_current_coord(entity, self.map)]


class Simulation:
    """Главный класс приложения, включает в себя:

        Карту
        Счётчик ходов
        Рендер поля
        Actions - список действий, исполняемых перед
        стартом симуляции или на каждом ходу"""



    def __init__(self, width: int, height: int):
        self.map = Map(width, height)
        self._counter = 0
        self.init_actions: list = [
            InitAction(0.05, self.map, Grass),
            InitAction(0.05, self.map, Rock),
            InitAction(0.05, self.map, Tree),
            InitAction(0.05, self.map, Herbivore),
            InitAction(0.05, self.map, Predator)
        ]
        self.turn_actions: list = [
            FindDeadEntity(self.map),
            MoveEntity(self.map)
        ]

    def next_turn(self):
        """ Просимулировать и отрендерить один ход"""
        for action in self.turn_actions:
            action.do()

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
        action.do()

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
