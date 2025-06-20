from abc import ABC, abstractmethod

from simulation.coordinates import Point
from simulation.path_finder import PathFinder
from simulation.world_map import Map


class Entity(ABC): ...


class Grass(Entity):
    pass


class Rock(Entity):
    pass


class Tree(Entity):
    pass


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
