from simulation.actions.base import Actions
from simulation.entities import Entity
from simulation.world_map import Map


class ResourceBalancer(Actions):
    """Добавляет ресурсов, если их осталось мало"""
    def __init__(self, world_map: Map, resource: type[Entity], action: Actions):
        self.action = action
        self.world_map = world_map
        self.resource = resource

    def __call__(self):
        all_current_resource = [entity
                                for entity in self.world_map.get_all_entities()
                                if isinstance(entity, self.resource)]

        if len(all_current_resource) < 3:
            self.action()
