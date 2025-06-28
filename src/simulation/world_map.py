from simulation.coordinates import Point
from simulation.entities import Entity, Creature


class Map:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._entities: dict[Point, Entity] = {}

    def get_entity(self, coordinates: Point) -> Entity | None:
        return self._entities.get(coordinates)

    def get_used_points(self) -> tuple[Point, ...]:
        return tuple(self._entities.keys())

    def get_all_entities(self) -> tuple[Entity, ...]:
        return tuple(self._entities.values())

    def get_creatures(self) -> list[Creature]:
        return [creature for creature in self.get_all_entities() if isinstance(creature, Creature)]

    def get_entity_point(self, target_entity: Entity) -> Point | None:
        """Возвращает значение координат объекта target_entity из map_object"""
        for coord, entity in self._entities.items():
            if entity == target_entity:
                return coord
        return None

    def get_resource(self, resource_type: type[Entity]) -> list[tuple[Point, Entity]]:
        return [(point, entity) for point, entity in self._entities.items() if isinstance(entity, resource_type)]

    def add_entity(self, coordinates: Point, entity: Entity) -> None:
        self._entities[coordinates] = entity

    def remove_entity(self, coordinates: Point):
        if coordinates in self._entities:
            del self._entities[coordinates]
