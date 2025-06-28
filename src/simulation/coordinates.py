from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Point:
    x: int
    y: int
