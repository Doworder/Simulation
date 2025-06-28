from heapq import heappop
from collections import deque
from typing import Deque

from simulation.coordinates import Point


class PathFinderBFS:
    """Класс для поиска пути с использованием алгоритма BFS"""

    def __call__(
            self,
            start_point: Point,
            map_object: "Map",
            resource_type: type["Entity"],
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

            neighbors = self._get_neighbors(
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


class PathFinderAstar:
    def __call__(
            self,
            start_point: Point,
            map_object: "Map",
            resource_type: type["Entity"],
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

        processed: set[Point] = set()
        search_queue: list[tuple[int, int, Point, list[Point]]] = [(1, 0, start_point, [])]
        target_point: Point = self._find_target(map_object, start_point, resource_type)
        while search_queue:
            _, g, current_point, current_path = heappop(search_queue)

            if current_point == target_point:
                return current_path + [current_point]

            if current_point in processed:
                continue

            processed.add(current_point)

            if current_point in map_object.get_used_points() and current_point != start_point:
                continue

            neighbors = self._get_neighbors(current_point, target_point, current_path, g, width, height)
            search_queue += neighbors

        return None

    def _find_target(
            self,
            map_object: "Map",
            coordinate: Point,
            entity_type: type["Entity"]
    ) -> Point:
        """Возвращает координаты приоритетной цели.
           Цель выбирается по минимальному расстоянию"""

        target_resource: list[tuple[Point, "Entity"]] = map_object.get_resource(entity_type)
        target_in_weights: list[tuple[int, Point]] = []
        for point, _ in target_resource:
            target_in_weights.append((self._heuristic(coordinate, point), point))

        _, target = min(target_in_weights, key=lambda h: h[0])

        return target

    def _get_neighbors(
            self,
            point: Point,
            target: Point,
            path: list[Point],
            g: int,
            width: int,
            height: int
    ) -> list[tuple[int, int, Point, list[Point]]]:
        """
        Получение соседних клеток с проверкой границ карты
        :param point: Текущая точка
        :param target: Целевая точка
        :param path: Текущий путь
        :param g: Стоимость пути
        :param width: Ширина карты
        :param height: Высота карты
        :return: Список соседних точек с обновленным путем, стоимостью шага, h(n)
        """
        offsets = ((0, 1), (1, 0), (0, -1), (-1, 0))  # Смещения для соседних клеток
        neighbors = []

        for dx, dy in offsets:
            x, y = point.x + dx, point.y + dy
            if 0 <= x < width and 0 <= y < height:
                new_point = Point(x, y)
                h = self._heuristic(new_point, target)
                neighbors.append((h, g+1, new_point, path + [point]))

        return neighbors

    @staticmethod
    def _heuristic(current: Point, target: Point) -> int:
        return abs(current.x - target.x) + abs(current.y - target.y)

