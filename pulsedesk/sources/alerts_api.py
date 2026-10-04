"""Fuente simulada de alertas."""

import asyncio
import logging
from datetime import datetime

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import AlertEvent
from pulsedesk.sources.base import EventSource


logger = logging.getLogger(__name__)


class AlertsApiSource(EventSource):
    """Simula la recepción periódica de alertas desde una API."""

    def __init__(
        self,
        event_bus: EventBus,
        interval: float = 5.0,
    ) -> None:
        super().__init__("alerts_api")
        self._event_bus = event_bus
        self._interval = interval

    async def start(self) -> None:
        """Inicia la fuente de alertas."""

        self._running = True

        logger.info("Fuente Alerts API iniciada.")

        try:
            while self._running:
                event = AlertEvent(
                    timestamp=datetime.now(),
                    source=self.name,
                    message="Alerta de prueba recibida.",
                    severity="WARNING",
                )

                await self._event_bus.publish(event)

                await asyncio.sleep(self._interval)

        except asyncio.CancelledError:
            logger.info("Fuente Alerts API cancelada.")
            raise

        finally:
            self._running = False

    async def stop(self) -> None:
        """Detiene la fuente de alertas."""

        self._running = False

        logger.info("Fuente Alerts API detenida.")