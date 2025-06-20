from __future__ import annotations
from pathlib import Path
from threading import Thread

from simulation.actions import Actions, SpawnEntity, ResourceBalancer, FindDeadEntity, MoveEntity
from simulation.config import load_config
from simulation.entities import Entity, Rock, Tree, Grass, Herbivore, Predator
from simulation.factories import RockFactory, TreeFactory, GrassFactory, HerbivoreFactory, PredatorFactory
from simulation.renderer import Renderer
from simulation.simulation import Simulation
from simulation.world_map import Map


def launcher(process: Simulation, renderer: Renderer) -> None:
    renderer.preview()
    while True:
        pause_flag = False
        user_input = input().lower()
        match user_input:
            case "e":
                process.stop_simulation()
                break

            case "p":
                pause_flag = True
                process.pause_simulation()
                renderer.paused()

            case "n":
                process.next_turn()
                renderer.nexted()

            case "s":
                if pause_flag:
                    pause_flag = False
                    process.resume_simulation()
                else:
                    process.start_simulation()


def main():
    config = load_config(Path("config.example.toml"))

    world = Map(config.world.width, config.world.height)

    rendering_simbols: dict[type[Entity], str] = {
        Rock: config.icons.rock,
        Tree: config.icons.tree,
        Grass: config.icons.grass,
        Herbivore: config.icons.herbivore,
        Predator: config.icons.predator
    }
    default_symbol: str = config.icons.default

    renderer = Renderer(world, rendering_simbols, default_symbol)

    init_actions: list[Actions] = [
            SpawnEntity(config.spawn_limit.rock, world, RockFactory()),
            SpawnEntity(config.spawn_limit.tree, world, TreeFactory()),
            SpawnEntity(config.spawn_limit.grass, world, GrassFactory()),
            SpawnEntity(
                config.spawn_limit.herbivore,
                world,
                HerbivoreFactory(config.herbivore.health, config.herbivore.speed)),
            SpawnEntity(
                config.spawn_limit.predator,
                world,
                PredatorFactory(config.predator.health, config.predator.speed, config.predator.attack_power))
        ]

    turn_actions: list[Actions] = [
            ResourceBalancer(world, Grass, SpawnEntity(config.balance_grass.count, world, GrassFactory())),
            ResourceBalancer(world, Herbivore, SpawnEntity(config.balance_herbivore.count, world, HerbivoreFactory(10, 1))),
            FindDeadEntity(world),
            MoveEntity(world)
        ]

    world_simulation = Simulation(init_actions, turn_actions, world, renderer)

    simulation = Thread(target=launcher, args=(world_simulation, renderer))
    simulation.start()

if __name__ == '__main__':
    main()