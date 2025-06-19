from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class WorldConfig:
    width: int
    height: int


@dataclass
class HerbivoreConfig:
    health: int
    speed: int

@dataclass
class PredatorConfig:
    health: int
    speed: int
    attack_power: int


@dataclass
class SpawnInitConfig:
    predator: int
    herbivore: int
    tree: int
    grass: int
    rock: int


@dataclass
class GrassTurnConfig:
    count: int


@dataclass
class HerbivoreTurnConfig:
    count: int


@dataclass
class Icons:
    predator: str
    herbivore: str
    tree: str
    grass: str
    rock: str
    default : str



print(data.items())
world = data['world']
herbivore = data['herbivore']
predator = data['predator']
spawn_limit = data['spawn_limit']
icons = data['icons']
print(world, herbivore, predator, spawn_limit, icons, sep='\n')