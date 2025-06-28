from simulation.actions.base import Actions
from simulation.world_map import Map


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
