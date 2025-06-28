from dataclasses import dataclass
from enum import Enum, auto


class Status(Enum):
    INIT = auto()
    STEP = auto()
    START = auto()
    PAUSE = auto()
    STOP = auto()


@dataclass
class Condition:
    status: Status = Status.INIT
