from typing import ValuesView, KeysView

from simulation.coordinates import Point
from simulation.entities import Entity, Creature


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

    def remove_entity(self, coordinates: Point):
        if coordinates in self._entities:
            del self._entities[coordinates]
