"""Punto de entrada de PulseDesk RAD."""

import asyncio
import logging

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import HeartbeatEvent
from pulsedesk.core.loop import PulseDeskLoop
from pulsedesk.core.state import AppState


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


async def heartbeat_handler(
    event: HeartbeatEvent,
    state: AppState,
) -> None:
    """Procesa eventos de heartbeat."""

    state.register_event(event.source)

    logging.info(
        "Heartbeat recibido | fuente=%s | eventos=%d",
        event.source,
        state.events_processed,
    )


async def run() -> None:
    """Ejecuta PulseDesk."""

    event_bus = EventBus()
    state = AppState()

    async def handle_heartbeat(event: HeartbeatEvent) -> None:
        await heartbeat_handler(event, state)

    event_bus.subscribe(
        HeartbeatEvent,
        handle_heartbeat,
    )

    loop = PulseDeskLoop(
        event_bus=event_bus,
        state=state,
    )

    try:
        await loop.start()

    except asyncio.CancelledError:
        loop.stop()
        raise


def main() -> None:
    """Punto de entrada de la aplicación."""

    try:
        asyncio.run(run())

    except KeyboardInterrupt:
        logging.info("Cierre solicitado por el usuario.")


if __name__ == "__main__":
    main()