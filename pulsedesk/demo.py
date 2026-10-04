"""Demostración integrada de PulseDesk."""

import asyncio
import logging

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import AlertEvent, HeartbeatEvent, TelemetryEvent
from pulsedesk.core.loop import PulseDeskLoop
from pulsedesk.core.state import AppState
from pulsedesk.sources.alerts_api import AlertsApiSource
from pulsedesk.sources.heartbeat import HeartbeatSource
from pulsedesk.sources.telemetry_file import TelemetryFileSource
from pulsedesk.ui.bridge import UiBridge
from pulsedesk.ui.console import ConsoleDashboard


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


async def run() -> None:
    """Ejecuta la demostración integrada."""

    event_bus = EventBus()
    state = AppState()

    bridge = UiBridge(state)
    dashboard = ConsoleDashboard()

    bridge.add_listener(dashboard.update)

    async def handle_heartbeat(event: HeartbeatEvent) -> None:
        bridge.handle_heartbeat(event)

    async def handle_telemetry(event: TelemetryEvent) -> None:
        bridge.handle_telemetry(event)

    async def handle_alert(event: AlertEvent) -> None:
        bridge.handle_alert(event)

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

    await loop.start()


def main() -> None:
    """Punto de entrada."""

    try:
        asyncio.run(run())

    except KeyboardInterrupt:
        print("\nPulseDesk detenido correctamente.")


if __name__ == "__main__":
    main()