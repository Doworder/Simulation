from __future__ import annotations
from abc import ABC, abstractmethod
from typing import ValuesView, KeysView, Deque
from dataclasses import dataclass
from random import randrange
from collections import deque
from threading import Thread, Event
import time


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class Entity(ABC): ...


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


class PathFinder:
    """Класс для поиска пути с использованием алгоритма BFS"""

    def __call__(
            self,
            start_point: Point,
            map_object: Map,
            resource_type: type[Entity],
            width: int,
            height: int
    ) -> list[Point] | None:
        """
        Поиск пути к ближайшему ресурсу указанного типа
        :param start_point: Точка старта
        :param map_object: Объект карты
        :param resource_type: Тип искомого ресурса
        :param width: Ширина карты
        :param height: Высота карты
        :return: Список точек пути или None, если путь не найден
        """
        processed = []
        search_queue: Deque = deque()
        search_queue.append((start_point, []))

        while search_queue:
            current_point, current_path = search_queue.popleft()

            if current_point in processed:
                continue

            processed.append(current_point)

            entity = map_object.get_entity(current_point)
            if isinstance(entity, resource_type):
                return current_path + [current_point]

            if entity and current_point != start_point:
                continue

            neighbors = PathFinder._get_neighbors(
                current_point,
                current_path,
                width,
                height
            )
            search_queue += neighbors

        return None

    @staticmethod
    def _get_neighbors(
            point: Point,
            path: list[Point],
            width: int,
            height: int
    ) -> list[tuple[Point, list[Point]]]:
        """
        Получение соседних клеток с проверкой границ карты
        :param point: Текущая точка
        :param path: Текущий путь
        :param width: Ширина карты
        :param height: Высота карты
        :return: Список соседних точек с обновленным путем
        """
        offsets = ((0, 1), (1, 0), (0, -1), (-1, 0))  # Смещения для соседних клеток
        neighbors = []

        for dx, dy in offsets:
            x, y = point.x + dx, point.y + dy
            if 0 <= x < width and 0 <= y < height:
                new_point = Point(x, y)
                neighbors.append((new_point, path + [point]))

        return neighbors


class Creature(Entity):
    def __init__(self, speed: int, health: int, target: type[Entity]):
        self.speed = speed
        self.hp = health
        self.target = target
        self._path_finder = PathFinder()

    @abstractmethod
    def target_interaction_handler(self, map_object: Map, target_point: Point):
        """Обработка взаимодействия с целью при достижении"""
        pass

    def make_move(self, map_object: Map) -> None:
        """Общая логика перемещения для всех существ"""
        resource_type = self.get_target_resource()
        path: list[Point] | None = self.find_path_to_resource(map_object, resource_type)
        if path is None:
            return

        current_point = path[0]
        current_entity: Entity | None = map_object.get_entity(current_point)

        # Если цель в соседней клетке
        if len(path) == 2:
            self.target_interaction_handler(map_object, path[-1])
            return

        # Определяем точку, в которую перемещаемся
        if len(path) <= self.speed:
            new_point = path[-2]  # Подходим вплотную к цели
        else:
            new_point = path[self.speed]  # Идем с максимальной скоростью

        # Перемещаем существо
        map_object.remove_entity(current_point)
        map_object.add_entity(new_point, current_entity)

        # Если после перемещения цель рядом - взаимодействуем
        new_path = self.find_path_to_resource(map_object, resource_type)
        if new_path and len(new_path) == 2:
            self.target_interaction_handler(map_object, new_path[-1])

    def get_target_resource(self) -> type[Entity]:
        """Возвращает класс ресурса, за которым охотится существо"""
        return self.target

    def find_path_to_resource(self, map_object: Map, resource: type[Entity]) -> list[Point] | None:
        """
        Поиск пути к ресурсу с использованием PathFinder
        :param map_object: Объект карты
        :param resource: Тип искомого ресурса
        :return: Список точек пути или None
        """
        current_point = map_object.get_entity_point(self)
        if current_point is None:
            return None

        return self._path_finder(
            start_point=current_point,
            map_object=map_object,
            resource_type=resource,
            width=map_object.width,
            height=map_object.height
        )


class Herbivore(Creature):
    def __init__(self, speed: int, health: int):
        super().__init__(speed, health, Grass)

    def target_interaction_handler(self, map_object: Map, target_point: Point):
        """Обработка взаимодействия с целью при достижении"""
        map_object.remove_entity(target_point)

    def attacked(self, attack_power: int):
        self.hp -= attack_power


class Predator(Creature):
    def __init__(self, speed: int, health: int, attack_power: int):
        super().__init__(speed, health, Herbivore)
        self.ap = attack_power

    def target_interaction_handler(self, map_object: Map, target_point: Point):
        """Хищник атакует травоядное"""
        target_entity = map_object.get_entity(target_point)
        if isinstance(target_entity, Herbivore):
            target_entity.attacked(self.ap)


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
    def __call__(self) -> None:
        pass


class SpawnEntity(Actions):
    def __init__(self, spawn_limit: int, map_object: Map, entity_factory: EntityFactory):
        self.spawn_limit = spawn_limit
        self.map_object = map_object
        self.entity_factory = entity_factory

    def __call__(self) -> None:
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

    def __call__(self) -> None:
        for entity in self.map_object.get_creatures():
            entity.make_move(self.map_object)


class FindDeadEntity(Actions):
    def __init__(self, map_object: Map):
        self.map_object = map_object

    @staticmethod
    def _is_dead(entity) -> bool:
        if entity.hp <= 0:
            return True
        return False

    def __call__(self):
        creatures = self.map_object.get_creatures()
        for entity in creatures:
            if self._is_dead(entity):
                point = self.map_object.get_entity_point(entity)
                self.map_object.remove_entity(point)


class Renderer:
    """Выполняет отрисовку в консоле"""
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

    def __init__(self, world_map: Map):
        self._map = world_map

    def _render(self):
        """Сделать отдельный класс"""
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


class Simulation:
    """Главный класс приложения, включает в себя:

        Карту
        Счётчик ходов
        Рендер поля
        Actions - список действий, исполняемых перед
        стартом симуляции или на каждом ходу"""



    def __init__(
            self,
            init_actions: list[Actions],
            turn_actions: list[Actions],
            world_map: Map,
            renderer: Renderer
    ):
        self._map = world_map
        self._counter = 0
        self._event = Event()
        self._tread =None
        self._simulation_flag = True
        self._init_actions = init_actions
        self._turn_actions = turn_actions
        self._renderer = renderer

        for action in self._init_actions:
            action.do()

    def next_turn(self):
        """ Просимулировать и отрендерить один ход"""
        for action in self._turn_actions:
            action.do()

        self._counter += 1
        #self._renderer.nexted()

    def _next_turn_loop(self):
        while self._simulation_flag:
            self._event.wait()
            self.next_turn()
            self._renderer.started()
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


def launcher(process: Simulation, renderer: Renderer) -> None:
    """Засунуть в Render!?"""
    renderer.preview()
    while True:
        pause_flag = False
        user_input = input().lower()
        match user_input:
            case "e":
                print("stop_flag = 'stop'")
                process.stop_simulation()
                break

            case "p":
                print("stop_flag = 'pause'")
                pause_flag = True
                process.pause_simulation()
                renderer.paused()

            case "n":
                print("stop_flag = 'next'")
                process.next_turn()
                renderer.nexted()

            case "s":
                if pause_flag:
                    print("stop_flag = 'resume'")
                    pause_flag = False
                    process.resume_simulation()
                else:
                    print("stop_flag = 'start'")
                    process.start_simulation()


if __name__ == '__main__':
    world = Map(15, 10)
    renderer = Renderer(world)

    init_actions: list[Actions] = [
            SpawnEntity(8, world, RockFactory()),
            SpawnEntity(7, world, TreeFactory()),
            SpawnEntity(15, world, GrassFactory()),
            SpawnEntity(15, world, HerbivoreFactory(10, 1)),
            SpawnEntity(10, world, PredatorFactory(10, 3, 3))
        ]

    turn_actions: list[Actions] = [
            FindDeadEntity(world),
            MoveEntity(world)
        ]

    world_simulation = Simulation(init_actions, turn_actions, world, renderer)

    simulation = Thread(target=launcher, args=(world_simulation, renderer))
    simulation.start()
