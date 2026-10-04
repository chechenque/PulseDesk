"""Handlers de eventos de PulseDesk."""

from pulsedesk.core.events import (
    AlertEvent,
    HeartbeatEvent,
    TelemetryEvent,
)
from pulsedesk.core.state import AppState
from pulsedesk.ui.bridge import UiBridge


class PulseDeskEventHandlers:
    """Procesa los eventos del dominio y actualiza el estado."""

    def __init__(
        self,
        state: AppState,
        bridge: UiBridge,
    ) -> None:
        self._state = state
        self._bridge = bridge

    async def handle_heartbeat(
        self,
        event: HeartbeatEvent,
    ) -> None:
        """Procesa un heartbeat."""

        self._bridge.handle_heartbeat(event)

    async def handle_telemetry(
        self,
        event: TelemetryEvent,
    ) -> None:
        """Procesa un evento de telemetría."""

        self._bridge.handle_telemetry(event)

    async def handle_alert(
        self,
        event: AlertEvent,
    ) -> None:
        """Procesa una alerta."""

        self._bridge.handle_alert(event)