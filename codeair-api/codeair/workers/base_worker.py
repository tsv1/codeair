from abc import ABC, abstractmethod

__all__ = ["BaseWorker"]


class BaseWorker(ABC):
    @abstractmethod
    async def run(self) -> None:
        pass
