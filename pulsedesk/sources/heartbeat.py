"""Fuente periódica de eventos heartbeat."""

import asyncio
import logging
from datetime import datetime

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import HeartbeatEvent
from pulsedesk.sources.base import EventSource

logger = logging.getLogger(__name__)


class HeartbeatSource(EventSource):
    """Genera eventos heartbeat periódicamente."""

    def __init__(
        self,
        event_bus: EventBus,
        interval: float = 1.0,
    ) -> None:
        super().__init__("heartbeat")
        self._event_bus = event_bus
        self._interval = interval

    async def start(self) -> None:
        """Inicia la generación de heartbeats."""

        self._running = True

        logger.info(
            "Fuente heartbeat iniciada | intervalo=%.1fs",
            self._interval,
        )

        try:
            while self._running:
                event = HeartbeatEvent(
                    timestamp=datetime.now(),
                    source=self.name,
                )

                await self._event_bus.publish(event)

                await asyncio.sleep(self._interval)

        except asyncio.CancelledError:
            logger.info("Fuente heartbeat cancelada.")
            raise

        finally:
            self._running = False

    async def stop(self) -> None:
        """Detiene la fuente heartbeat."""

        self._running = False

        logger.info("Fuente heartbeat detenida.")
