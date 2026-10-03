"""Ciclo principal asíncrono de PulseDesk."""

import asyncio
import logging
from datetime import datetime

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import HeartbeatEvent
from pulsedesk.core.state import AppState


logger = logging.getLogger(__name__)


class PulseDeskLoop:
    """Coordina el ciclo de ejecución de PulseDesk."""

    def __init__(
        self,
        event_bus: EventBus,
        state: AppState,
    ) -> None:
        self._event_bus = event_bus
        self._state = state
        self._running = False

    async def start(self) -> None:
        """Inicia el ciclo principal."""

        self._running = True
        self._state.set_running(True)

        logger.info("PulseDesk iniciado.")

        try:
            while self._running:
                event = HeartbeatEvent(
                    timestamp=datetime.now(),
                )

                await self._event_bus.publish(event)

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info("Loop cancelado.")
            raise

        finally:
            self._running = False
            self._state.set_running(False)

            logger.info("PulseDesk detenido.")

    def stop(self) -> None:
        """Solicita detener el ciclo."""

        self._running = False