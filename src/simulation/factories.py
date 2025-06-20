from abc import abstractmethod

from simulation.entities import Entity, Rock, Tree, Grass, Herbivore, Predator


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
