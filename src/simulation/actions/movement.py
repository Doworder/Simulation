from simulation.actions.base import Actions
from simulation.world_map import Map


class MoveEntity(Actions):
    def __init__(self, map_object: Map):
        self.map_object = map_object

    def __call__(self) -> None:
        for entity in self.map_object.get_creatures():
            entity.make_move(self.map_object)
