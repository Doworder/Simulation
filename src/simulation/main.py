from __future__ import annotations
from abc import ABC, abstractmethod
from typing import ValuesView, KeysView
from dataclasses import dataclass
from random import randrange
from collections import deque
from threading import Thread, Event
import time


@dataclass(frozen=True)
class Point:
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
        self._entities: dict[Point, Entity] = {}
        self._creatures: set = set()

    def get_entity(self, coordinates: Point) -> Entity | None:
        return self._entities.get(coordinates)

    def get_used_points(self) -> KeysView[Point]:
        return self._entities.keys()

    def get_all_entities(self) -> ValuesView[Entity]:
        return self._entities.values()

    def get_creatures(self) -> list[Creature]:
        return [creature for creature in self.get_all_entities() if isinstance(creature, Creature)]

    def get_entity_point(self, value: Entity) -> Point | None:
        """Возвращает значение координат объекта value из map_object"""
        for coord, entity in self._entities.items():
            if entity == value:
                return coord
        return None

    def add_entity(self, coordinates: Point, entity: Entity) -> None:
        self._entities[coordinates] = entity
        if isinstance(entity, Creature):
            self._creatures.add(entity)

    def remove_entity(self, coordinates: Point):
        if coordinates in self._entities:
            del self._entities[coordinates]


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
    def make_move(self, map_object: Map) -> None:
        pass

    def find_path_to_resource(self, map_object: Map, resource: type[Entity]) -> list[Point] | None:
        processed: list = []
        coord = map_object.get_entity_point(self)
        if coord is None:
            return None
        search_queue = deque()  # type: ignore
        search_queue.append((coord, []))
        while search_queue:
            entity_coord, path_to_resource = search_queue.popleft()
            if entity_coord in processed:
                continue

            processed.append(entity_coord)

            if isinstance(map_object.get_entity(entity_coord), resource):
                path_to_resource.append(entity_coord)
                return path_to_resource

            if isinstance(map_object.get_entity(entity_coord), Entity):
                if entity_coord is not coord:
                    continue

            neighbors = self.get_neighbors(entity_coord, path_to_resource, map_object)
            search_queue += neighbors

        return None

    @staticmethod
    def get_neighbors(coords: Point, path: list, map_object: Map) -> list:
        neighbors_coords = [
            (coords.x, coords.y+1),
            (coords.x+1, coords.y),
            (coords.x, coords.y-1),
            (coords.x-1, coords.y)
        ]
        return [(Point(x, y), path + [coords]) for x, y in neighbors_coords if (0 <= x < map_object.width and 0 <= y < map_object.height)]


class Herbivore(Creature):
    def __init__(self, speed: int, health: int):
        super().__init__(speed, health)

    def make_move(self, map_object: Map):
        """Выполнить ход, либо съесть травы"""
        path: list[Point] | None = self.find_path_to_resource(map_object, Grass)
        if path is None:
            return

        if len(path) == 2:
            map_object.remove_entity(path[-1])

        elif len(path) <= self.speed:
            current_entity = map_object.get_entity(path[0])
            map_object.remove_entity(path[0])
            map_object.add_entity(path[-2], current_entity)

        else:
            current_entity = map_object.get_entity(path[0])
            map_object.remove_entity(path[0])
            map_object.add_entity(path[self.speed], current_entity)

    def attacked(self, attack_power: int):
        self.hp -= attack_power


class Predator(Creature):
    def __init__(self, speed: int, health: int, attack_power: int):
        super().__init__(speed, health)
        self.ap = attack_power

    def make_move(self, map_object: Map):
        """Выполнить ход, атаковать"""
        path: list[Point] | None = self.find_path_to_resource(map_object, Herbivore)
        if path is None:
            return

        if len(path) == 2:
            target_entity: Herbivore = map_object.get_entity(path[-1])
            target_entity.attacked(self.ap)

        elif len(path) <= self.speed:
            current_entity = map_object.get_entity(path[0])
            map_object.remove_entity(path[0])
            map_object.add_entity(path[-2], current_entity)
            target_entity = map_object.get_entity(path[-1])
            target_entity.attacked(self.ap)

        else:
            current_entity = map_object.get_entity(path[0])
            map_object.remove_entity(path[0])
            map_object.add_entity(path[self.speed], current_entity)


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
    def __init__(self, spawn_limit: int, map_object: Map, entity_factory: EntityFactory):
        self.spawn_limit = spawn_limit
        self.map_object = map_object
        self.entity_factory = entity_factory

    def do(self) -> None:
        while self.spawn_limit:
            entity = self.entity_factory.create_entity()
            coordinate = Point(randrange(0, self.map_object.width), randrange(0, self.map_object.height))
            if coordinate in self.map_object.get_used_points():
                continue
            self.map_object.add_entity(coordinate, entity)
            self.spawn_limit -= 1


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
    def __init__(self, map_object: Map):
        self.map_object = map_object

    def do(self) -> None:
        for entity in self.map_object.get_creatures():
            entity.make_move(self.map_object)


class FindDeadEntity(Actions):
    def __init__(self, map_object: Map):
        self.map_object = map_object

    @staticmethod
    def is_dead(entity) -> bool:
        if entity.hp > 0:
            return False
        return True

    def do(self):
        creatures = self.map_object.get_creatures()
        for entity in creatures:
            if self.is_dead(entity):
                point = self.map_object.get_entity_point(entity)
                self.map_object.remove_entity(point)


class Simulation:
    """Главный класс приложения, включает в себя:

        Карту
        Счётчик ходов
        Рендер поля
        Actions - список действий, исполняемых перед
        стартом симуляции или на каждом ходу"""



    def __init__(self, width: int, height: int):
        self._map = Map(width, height)
        self._counter = 0
        self._event = Event()
        self._tread =None
        self._simulation_flag = True
        self.init_actions: list = [
            SpawnEntity(8, self._map, RockFactory()),
            SpawnEntity(7, self._map, TreeFactory()),
            SpawnEntity(15, self._map, GrassFactory()),
            SpawnEntity(15, self._map, HerbivoreFactory(10, 1)),
            SpawnEntity(10, self._map, PredatorFactory(10, 3, 3))
        ]
        self.turn_actions: list = [
            FindDeadEntity(self._map),
            MoveEntity(self._map)
        ]

        for action in self.init_actions:
            action.do()

    def next_turn(self):
        """ Просимулировать и отрендерить один ход"""
        for action in self.turn_actions:
            action.do()

        self._counter += 1
        self.map_renderer()

    def _next_turn_loop(self):
        while self._simulation_flag:
            self._event.wait()
            self.next_turn()
            time.sleep(1)


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
        width = self._map.width
        height = self._map.height
        rendering_symbols = {
            Predator: 'P ',
            Herbivore: 'H ',
            Grass: 'G ',
            Rock: 'R ',
            Tree: 'T '
        }

        for j in range(height):
            for i in range(width):
                coord = Point(i, j)
                if coord not in self._map.get_used_points():
                    print('* ', end='')
                else:
                    entity = self._map.get_entity(coord)
                    print(rendering_symbols[entity.__class__], end='')
            print()
        print(self._counter)


def processing_user_commands(work_object: Simulation) -> None:
    while True:
        pause_flag = False
        user_input = input("""
        Press (S, Enter) to start or (N, Enter) to one cicle
        Press (P, Enter) to pause or (E, Enter) to exit""").lower()
        match user_input:
            case "e":
                print("stop_flag = 'stop'")
                work_object.stop_simulation()
                break

            case "p":
                print("stop_flag = 'pause'")
                pause_flag = True
                work_object.pause_simulation()

            case "n":
                print("stop_flag = 'next'")
                work_object.next_turn()

            case "s":
                if pause_flag:
                    print("stop_flag = 'resume'")
                    pause_flag = False
                    work_object.resume_simulation()
                else:
                    print("stop_flag = 'start'")
                    work_object.start_simulation()


if __name__ == '__main__':
    world = Simulation(15, 10)

    print()
    world.map_renderer()

    simulation = Thread(target=processing_user_commands, args=(world, ))
    simulation.start()
