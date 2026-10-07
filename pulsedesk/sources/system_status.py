"""Fuente de eventos de estado del sistema."""

import asyncio
import logging
from datetime import datetime

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import TelemetryEvent
from pulsedesk.sources.base import EventSource

logger = logging.getLogger(__name__)


class SystemStatusSource(EventSource):
    """Genera periódicamente información del estado del sistema."""

    def __init__(
        self,
        event_bus: EventBus,
        interval: float = 4.0,
    ) -> None:
        super().__init__("system_status")
        self._event_bus = event_bus
        self._interval = interval

    async def start(self) -> None:
        """Inicia la generación de eventos de estado."""

        self._running = True

        logger.info("Fuente de estado del sistema iniciada.")

        try:
            while self._running:
                event = TelemetryEvent(
                    timestamp=datetime.now(),
                    source=self.name,
                    metric="status",
                    value="OK",
                )

                await self._event_bus.publish(event)

                await asyncio.sleep(self._interval)

        except asyncio.CancelledError:
            logger.info("Fuente de estado del sistema cancelada.")
            raise

        finally:
            self._running = False

    async def stop(self) -> None:
        """Detiene la fuente."""

        self._running = False

        logger.info("Fuente de estado del sistema detenida.")
