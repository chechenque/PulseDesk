"""Puente entre el núcleo asíncrono y la interfaz."""

from collections.abc import Callable

from pulsedesk.core.events import AlertEvent, HeartbeatEvent, TelemetryEvent
from pulsedesk.core.state import AppState
from pulsedesk.ui.model import DashboardData


class UiBridge:
    """Transforma eventos del dominio en datos para la UI."""

    def __init__(self, state: AppState) -> None:
        self._state = state
        self._listeners: list[Callable[[DashboardData], None]] = []

    def add_listener(
        self,
        listener: Callable[[DashboardData], None],
    ) -> None:
        """Registra un listener de cambios."""

        if listener not in self._listeners:
            self._listeners.append(listener)

    def remove_listener(
        self,
        listener: Callable[[DashboardData], None],
    ) -> None:
        """Elimina un listener."""

        if listener in self._listeners:
            self._listeners.remove(listener)

    def handle_heartbeat(self, event: HeartbeatEvent) -> None:
        """Procesa un heartbeat para la UI."""

        self._state.register_event(event.source)
        self._notify()

    def handle_telemetry(self, event: TelemetryEvent) -> None:
        """Procesa telemetría para la UI."""

        self._state.register_event(event.source)
        self._notify()

    def handle_alert(self, event: AlertEvent) -> None:
        """Procesa una alerta para la UI."""

        self._state.register_event(event.source)
        self._state.alerts_active += 1
        self._notify()

    def snapshot(self) -> DashboardData:
        """Obtiene una copia del estado para mostrar."""

        return DashboardData(
            running=self._state.running,
            events_processed=self._state.events_processed,
            alerts_active=self._state.alerts_active,
            last_source=self._state.last_source or "-",
            last_event_at=self._state.last_event_at,
        )

    def _notify(self) -> None:
        """Notifica a los listeners."""

        data = self.snapshot()

        for listener in tuple(self._listeners):
            listener(data)