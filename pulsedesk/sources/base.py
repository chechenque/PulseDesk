"""Clases base para las fuentes de eventos."""

from abc import ABC, abstractmethod
from typing import Any


class EventSource(ABC):
    """Interfaz común para una fuente de eventos."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._running = False

    @property
    def running(self) -> bool:
        """Indica si la fuente está activa."""

        return self._running

    @abstractmethod
    async def start(self) -> None:
        """Inicia la fuente de eventos."""

    @abstractmethod
    async def stop(self) -> None:
        """Detiene la fuente de eventos."""
