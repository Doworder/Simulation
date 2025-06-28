from random import randrange

from simulation.actions.base import Actions
from simulation.coordinates import Point
from simulation.factories import EntityFactory
from simulation.world_map import Map


class SpawnEntity(Actions):
    def __init__(self, spawn_limit: int, map_object: Map, entity_factory: EntityFactory):
        self.spawn_limit = spawn_limit
        self.map_object = map_object
        self.entity_factory = entity_factory

    def __call__(self) -> None:
        counter: int = 0
        while counter < self.spawn_limit:
            entity = self.entity_factory.create_entity()
            coordinate = Point(randrange(0, self.map_object.width), randrange(0, self.map_object.height))
            if coordinate in self.map_object.get_used_points():
                continue
            self.map_object.add_entity(coordinate, entity)
            counter += 1
