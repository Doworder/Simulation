from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import randint
from collections import deque
from threading import Thread, Event


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
    def make_move(self, map: Map) -> None:
        pass

    def find_path_to_resource(self, map: Map, resource: type[Entity]) -> list[Coordinates] | None:
        processed: list = []
        coord: Coordinates | None = self.find_current_coord(self, map)
        search_queue: deque[tuple[Coordinates, list[Coordinates]]] = deque()
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

        return None

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
        path: list[Coordinates] | None = self.find_path_to_resource(map, Grass)
        if path is None:
            return

        if len(path) == 2:
            map.entities.pop(path[-1])

        elif len(path) <= self.speed:
            current_entity = map.entities.pop(path[0])
            map.entities[path[-2]] = current_entity

        else:
            current_entity = map.entities.pop(path[0])
            map.entities[path[self.speed]] = current_entity

    def attacked(self, attack_power: int):
        self.hp -= attack_power


class Predator(Creature):
    def __init__(self, speed: int, health: int, attack_power: int):
        super().__init__(speed, health)
        self.ap = attack_power

    def make_move(self, map: Map):
        """Выполнить ход, атаковать"""
        path: list[Coordinates] | None = self.find_path_to_resource(map, Herbivore)
        if path is None:
            return

        if len(path) == 2:
            map.entities[path[-1]].attacked(self.ap)

        elif len(path) <= self.speed:
            current_entity = map.entities.pop(path[0])
            map.entities[path[-2]] = current_entity
            map.entities[path[-1]].attacked(self.ap)

        else:
            current_entity = map.entities.pop(path[0])
            map.entities[path[self.speed]] = current_entity


class EntityFactory:
    @abstractmethod
    def create_entity(self) -> Entity: ...


class RockFactory(EntityFactory):
    def create_entity(self) -> Rock:
        return Rock()


class TreeFactory(EntityFactory):
    def create_entity(self) -> Tree:
        return Tree()


class GrassFactory(EntityFactory):
    def create_entity(self) -> Grass:
        return Grass()


class HerbivoreFactory(EntityFactory):
    def __init__(self, health: int, speed: int):
        self.health = health
        self.speed = speed
        self.resource = Grass

    def create_entity(self) -> Herbivore:
        return Herbivore(self.speed, self.health)


class PredatorFactory(EntityFactory):
    def __init__(self, health: int, speed: int, attack_power: int):
        self.health = health
        self.speed = speed
        self.ap = attack_power

    def create_entity(self) -> Predator:
        return Predator(self.speed, self.health, self.ap)


class Actions(ABC):
    @abstractmethod
    def do(self) -> None:
        pass


class SpawnEntity(Actions):
    def __init__(self, spawn_limit: int, world_map: Map, entity_factory: EntityFactory):
        self.spawn_limit = spawn_limit
        self.world_map = world_map
        self.entity_factory = entity_factory

    def do(self) -> None:
        while self.spawn_limit:
            entity = self.entity_factory.create_entity()
            coordinate = Coordinates(randint(0, self.world_map.width - 1), randint(0, self.world_map.height - 1))
            if coordinate in self.world_map.entities:
                continue
            self.world_map.add_entity(coordinate, entity)
            self.spawn_limit -= 1


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
        for entity in self.map.creatures.copy():
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
        self._event = Event()
        self._tread =None
        self._simulation_flag = True
        self.init_actions: list = [
            SpawnEntity(8, self.map, RockFactory()),
            SpawnEntity(7, self.map, TreeFactory()),
            SpawnEntity(15, self.map, GrassFactory()),
            SpawnEntity(15, self.map, HerbivoreFactory(10, 1)),
            SpawnEntity(10, self.map, PredatorFactory(10, 3, 3))
        ]
        self.turn_actions: list = [
            FindDeadEntity(self.map),
            MoveEntity(self.map)
        ]

        for action in self.init_actions:
            action.do()

    def next_turn(self):
        """ Просимулировать и отрендерить один ход"""
        for action in self.turn_actions:
            action.do()

        self.map_renderer()
        self._counter += 1

    def _next_turn_loop(self):
        while self._simulation_flag:
            self._event.wait()
            self.next_turn()


    def start_simulation(self):
        """- запустить бесконечный цикл симуляции и рендеринга"""
        self._event.set()
        self._tread = Thread(target=self._next_turn_loop, daemon=True)
        self._tread.start()

    def pause_simulation(self):
        """ - приостановить бесконечный цикл симуляции и рендеринга"""
        self._event.clear()

    def resume_simulation(self):
        """продолжить цикл симуляции и рендеринга"""
        self._event.set()

    def stop_simulation(self):
        """остановить бесконечный цикл симуляции и рендеринга"""
        self._simulation_flag = False

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

        for j in range(height):
            for i in range(width):
                coord = Coordinates(i, j)
                if coord not in self.map.entities:
                    print('* ', end='')
                else:
                    print(rendering_symbols[(self.map.entities[coord]).__class__], end='')
            print()
        print(self._counter)


def processing_user_commands(object: Simulation) -> None:
    while True:
        pause_flag = False
        user_input = input("""
        Press (S, Enter) to start or (N, Enter) to one cicle
        Press (P, Enter) to pause or (E, Enter) to exit""").lower()
        match user_input:
            case "e":
                print("stop_flag = 'stop'")
                object.stop_simulation()
                break

            case "p":
                print("stop_flag = 'pause'")
                pause_flag = True
                object.pause_simulation()

            case "n":
                print("stop_flag = 'next'")
                object.next_turn()

            case "s":
                if pause_flag:
                    print("stop_flag = 'resume'")
                    pause_flag = False
                    object.resume_simulation()
                else:
                    print("stop_flag = 'start'")
                    object.start_simulation()


if __name__ == '__main__':
    world = Simulation(15, 10)
    for action in world.init_actions:
        action.do()

    world.map_renderer()

    simulation = Thread(target=processing_user_commands, args=(world, )).start()
