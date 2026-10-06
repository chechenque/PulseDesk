"""Punto de entrada de la interfaz gráfica."""

from __future__ import annotations

import asyncio
import sys

from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import (
    AlertEvent,
    HeartbeatEvent,
    TelemetryEvent,
)
from pulsedesk.core.handlers import PulseDeskEventHandlers
from pulsedesk.core.loop import PulseDeskLoop
from pulsedesk.core.state import AppState
from pulsedesk.sources.alerts_api import AlertsApiSource
from pulsedesk.sources.heartbeat import HeartbeatSource
from pulsedesk.sources.system_status import SystemStatusSource
from pulsedesk.sources.telemetry_file import TelemetryFileSource
from pulsedesk.ui.app import DashboardWindow
from pulsedesk.ui.bridge import UiBridge


async def run(
    app: QApplication,
    window: DashboardWindow,
) -> None:
    """Ejecuta PulseDesk integrado con Qt."""

    event_bus = EventBus()
    state = AppState()

    bridge = UiBridge(state)
    bridge.add_listener(window.update_dashboard)

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

    state.set_running(True)
    window.show()

    try:
        await loop.start()

    except asyncio.CancelledError:
        pass

    finally:
        state.set_running(False)


def main() -> None:
    """Inicia la aplicación Qt."""

    app = QApplication(sys.argv)

    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    window = DashboardWindow()

    task = event_loop.create_task(
        run(app, window),
    )

    def shutdown() -> None:
        """Solicita el cierre limpio de PulseDesk."""

        if not task.done():
            task.cancel()

    app.aboutToQuit.connect(shutdown)

    with event_loop:
        event_loop.run_forever()


if __name__ == "__main__":
    main()