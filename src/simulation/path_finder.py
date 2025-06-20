from __future__ import annotations
from collections import deque
from typing import Deque

from simulation.coordinates import Point


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
