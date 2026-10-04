"""Fuente de telemetría basada en un archivo."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import TelemetryEvent
from pulsedesk.sources.base import EventSource


logger = logging.getLogger(__name__)


class TelemetryFileSource(EventSource):
    """Lee datos de telemetría desde un archivo."""

    def __init__(
        self,
        event_bus: EventBus,
        file_path: str | Path,
        interval: float = 2.0,
    ) -> None:
        super().__init__("telemetry_file")
        self._event_bus = event_bus
        self._file_path = Path(file_path)
        self._interval = interval
        self._position = 0

    async def start(self) -> None:
        """Inicia la lectura del archivo."""

        self._running = True

        logger.info(
            "Fuente de telemetría iniciada | archivo=%s",
            self._file_path,
        )

        try:
            while self._running:
                await self._read_new_data()
                await asyncio.sleep(self._interval)

        except asyncio.CancelledError:
            logger.info("Fuente de telemetría cancelada.")
            raise

        finally:
            self._running = False

    async def _read_new_data(self) -> None:
        """Lee nuevas líneas del archivo."""

        if not self._file_path.exists():
            return

        lines = self._file_path.read_text(
            encoding="utf-8",
        ).splitlines()

        new_lines = lines[self._position:]

        for line in new_lines:
            line = line.strip()

            if not line:
                continue

            event = TelemetryEvent(
                timestamp=datetime.now(),
                source=self.name,
                metric="message",
                value=line,
            )

            await self._event_bus.publish(event)

        self._position = len(lines)

    async def stop(self) -> None:
        """Detiene la fuente de telemetría."""

        self._running = False

        logger.info("Fuente de telemetría detenida.")