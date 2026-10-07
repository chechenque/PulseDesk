"""Demostración integrada de PulseDesk."""

import asyncio
import logging

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import AlertEvent, HeartbeatEvent, TelemetryEvent
from pulsedesk.core.handlers import PulseDeskEventHandlers
from pulsedesk.core.loop import PulseDeskLoop
from pulsedesk.core.state import AppState
from pulsedesk.sources.alerts_api import AlertsApiSource
from pulsedesk.sources.heartbeat import HeartbeatSource
from pulsedesk.sources.system_status import SystemStatusSource
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

    handlers = PulseDeskEventHandlers(
        state=state,
        bridge=bridge,
    )

    event_bus.subscribe(
        HeartbeatEvent,
        handlers.handle_heartbeat,
    )

    event_bus.subscribe(
        TelemetryEvent,
        handlers.handle_telemetry,
    )

    event_bus.subscribe(
        AlertEvent,
        handlers.handle_alert,
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
        SystemStatusSource(
            event_bus=event_bus,
            interval=4.0,
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
