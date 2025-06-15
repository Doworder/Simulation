from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


path = Path("config.example.toml")
with path.open(mode="rb") as f:
    data = tomllib.load(f)

print(data.items())
world = data['world']
herbivore = data['herbivore']
predator = data['predator']
spawn_limit = data['spawn_limit']
icons = data['icons']
print(world, herbivore, predator, spawn_limit, icons, sep='\n')