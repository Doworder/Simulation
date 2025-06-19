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


@dataclass
class Config:
    world: WorldConfig
    herbivore: HerbivoreConfig
    predator: PredatorConfig
    spawn_limit: SpawnInitConfig
    balance_grass: GrassTurnConfig
    balance_herbivore: HerbivoreTurnConfig
    icons: Icons


class ConfigCreator:
    def __init__(self):
        self.config = {}

    def __call__(self, data, cls) -> Config:
        for item in data.items():
            current_class = Config.__annotations__[item[0]]
            self.config[item[0]] = current_class(**item[1])

        return cls(**self.config)


config_creator = ConfigCreator()

def load_config(path: Path) -> Config:
    with path.open(mode="rb") as f:
        data = tomllib.load(f)

    config = config_creator(data, Config)

    return config
