"""Punto de entrada de PulseDesk RAD."""

import asyncio
import logging

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import AlertEvent, HeartbeatEvent, TelemetryEvent
from pulsedesk.core.loop import PulseDeskLoop
from pulsedesk.core.state import AppState
from pulsedesk.sources.alerts_api import AlertsApiSource
from pulsedesk.sources.heartbeat import HeartbeatSource
from pulsedesk.sources.telemetry_file import TelemetryFileSource

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


async def heartbeat_handler(
    event: HeartbeatEvent,
    state: AppState,
) -> None:
    """Procesa eventos heartbeat."""

    state.register_event(event.source)

    logging.info(
        "Heartbeat | eventos=%d",
        state.events_processed,
    )


async def telemetry_handler(
    event: TelemetryEvent,
    state: AppState,
) -> None:
    """Procesa eventos de telemetría."""

    state.register_event(event.source)

    logging.info(
        "Telemetría | %s=%s",
        event.metric,
        event.value,
    )


async def alert_handler(
    event: AlertEvent,
    state: AppState,
) -> None:
    """Procesa eventos de alerta."""

    state.register_event(event.source)
    state.alerts_active += 1

    logging.warning(
        "ALERTA [%s] | %s",
        event.severity,
        event.message,
    )


async def run() -> None:
    """Construye y ejecuta PulseDesk."""

    event_bus = EventBus()
    state = AppState()

    async def handle_heartbeat(event: HeartbeatEvent) -> None:
        await heartbeat_handler(event, state)

    async def handle_telemetry(event: TelemetryEvent) -> None:
        await telemetry_handler(event, state)

    async def handle_alert(event: AlertEvent) -> None:
        await alert_handler(event, state)

    event_bus.subscribe(
        HeartbeatEvent,
        handle_heartbeat,
    )

    event_bus.subscribe(
        TelemetryEvent,
        handle_telemetry,
    )

    event_bus.subscribe(
        AlertEvent,
        handle_alert,
    )

    sources = [
        HeartbeatSource(
            event_bus=event_bus,
            interval=1.0,
        ),
        TelemetryFileSource(
            event_bus=event_bus,
            file_path="data/telemetry.txt",
            interval=3.0,
        ),
        AlertsApiSource(
            event_bus=event_bus,
            interval=5.0,
        ),
    ]

    loop = PulseDeskLoop(sources)

    try:
        await loop.start()

    except asyncio.CancelledError:
        raise


def main() -> None:
    """Punto de entrada de la aplicación."""

    try:
        asyncio.run(run())

    except KeyboardInterrupt:
        logging.info("Cierre solicitado por el usuario.")


if __name__ == "__main__":
    main()
