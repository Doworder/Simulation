from abc import ABC, abstractmethod


class Actions(ABC):
    @abstractmethod
    def __call__(self) -> None:
        pass
