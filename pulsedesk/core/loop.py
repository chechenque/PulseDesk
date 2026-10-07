"""Ciclo principal asíncrono de PulseDesk."""

import asyncio
import logging

from pulsedesk.sources.base import EventSource

logger = logging.getLogger(__name__)


class PulseDeskLoop:
    """Coordina el ciclo de ejecución y las fuentes de eventos."""

    def __init__(
        self,
        sources: list[EventSource],
    ) -> None:
        self._sources = sources
        self._tasks: list[asyncio.Task[None]] = []
        self._running = False

    async def start(self) -> None:
        """Inicia todas las fuentes y mantiene activo el sistema."""

        if self._running:
            return

        self._running = True

        logger.info(
            "PulseDesk iniciado | fuentes=%d",
            len(self._sources),
        )

        self._tasks = [
            asyncio.create_task(
                source.start(),
                name=f"source-{source.name}",
            )
            for source in self._sources
        ]

        try:
            await asyncio.gather(*self._tasks)

        except asyncio.CancelledError:
            logger.info("Loop principal cancelado.")
            raise

        finally:
            await self.stop()

    async def stop(self) -> None:
        """Detiene todas las fuentes y cancela sus tareas."""

        if not self._running and not self._tasks:
            return

        self._running = False

        logger.info("Deteniendo fuentes...")

        for source in self._sources:
            await source.stop()

        current_task = asyncio.current_task()

        for task in self._tasks:
            if task is not current_task and not task.done():
                task.cancel()

        if self._tasks:
            await asyncio.gather(
                *self._tasks,
                return_exceptions=True,
            )

        self._tasks.clear()

        logger.info("PulseDesk detenido.")
