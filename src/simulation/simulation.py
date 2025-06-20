from datetime import time
from threading import Thread, Event

from simulation.actions import Actions
from simulation.renderer import Renderer
from simulation.world_map import Map


class Simulation:
    """Главный класс приложения, включает в себя:

        Карту
        Счётчик ходов
        Рендер поля
        Actions - список действий, исполняемых перед
        стартом симуляции или на каждом ходу"""



    def __init__(
            self,
            init_actions: list[Actions],
            turn_actions: list[Actions],
            world_map: Map,
            renderer: Renderer
    ):
        self._map = world_map
        self._counter = 0
        self._event = Event()
        self._tread =None
        self._simulation_flag = True
        self._init_actions = init_actions
        self._turn_actions = turn_actions
        self._renderer = renderer

        for action in self._init_actions:
            action()

    def next_turn(self):
        """ Отсимулировать и отрендерить один ход"""
        for action in self._turn_actions:
            action()

        self._counter += 1

    def _next_turn_loop(self):
        while self._simulation_flag:
            self._event.wait()
            self.next_turn()
            self._renderer.started()
            time.sleep(1)


    def start_simulation(self):
        """- запустить бесконечный цикл симуляции и рендеринга"""
        self._event.set()
        self._tread = Thread(target=self._next_turn_loop, daemon=True)
        self._tread.start()

    def pause_simulation(self):
        """ - приостановить бесконечный цикл симуляции и рендеринга"""
        self._event.clear()

    def resume_simulation(self):
        """продолжить цикл симуляции и рендеринга"""
        self._event.set()

    def stop_simulation(self):
        """остановить бесконечный цикл симуляции и рендеринга"""
        self._simulation_flag = False
