from abc import ABC


class Entity(ABC):
    pass


class Grass(Entity):
    pass


class Rock(Entity):
    pass


class Tree(Entity):
    pass


class Creature(Entity):
    pass


class Herbivore(Creature):
    pass


class Predator(Creature):
    pass


class Map:
class Simulation:
    """Главный класс приложения, включает в себя:

        Карту
        Счётчик ходов
        Рендерер поля
        Actions - список действий, исполняемых перед
        стартом симуляции или на каждом ходу"""


    def next_turn(self):
        """ росимулировать и отрендерить один ход"""

    def start_simulation(self):
        """- запустить бесконечный цикл симуляции и рендеринга"""

    def pause_simulation(self):
        """ - приостановить бесконечный цикл симуляции и рендеринга"""

