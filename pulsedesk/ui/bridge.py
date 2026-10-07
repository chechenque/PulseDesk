"""Puente entre el núcleo asíncrono y la interfaz."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from threading import Lock

from pulsedesk.core.events import AlertEvent, HeartbeatEvent, TelemetryEvent
from pulsedesk.core.state import AppState
from pulsedesk.ui.model import DashboardData


class UiBridge:
    """Transforma eventos del dominio en datos seguros para la UI."""

    def __init__(self, state: AppState) -> None:
        self._state = state
        self._listeners: list[Callable[[DashboardData], None]] = []
        self._lock = Lock()
        self._recent_events: deque[str] = deque(maxlen=10)

    def add_listener(
        self,
        listener: Callable[[DashboardData], None],
    ) -> None:
        """Registra un listener."""

        with self._lock:
            if listener not in self._listeners:
                self._listeners.append(listener)

    def remove_listener(
        self,
        listener: Callable[[DashboardData], None],
    ) -> None:
        """Elimina un listener."""

        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def handle_heartbeat(
        self,
        event: HeartbeatEvent,
    ) -> None:
        """Procesa un heartbeat."""

        self._state.register_event(event.source)
        self._add_event(
            event.source,
            "INFO",
        )
        self._notify()

    def handle_telemetry(
        self,
        event: TelemetryEvent,
    ) -> None:
        """Procesa telemetría."""

        self._state.register_event(event.source)
        self._add_event(
            event.source,
            "INFO",
        )
        self._notify()

    def handle_alert(
        self,
        event: AlertEvent,
    ) -> None:
        """Procesa una alerta."""

        self._state.register_event(event.source)
        self._state.alerts_active += 1

        self._add_event(
            event.source,
            event.severity,
        )

        self._notify()

    def _add_event(
        self,
        source: str,
        severity: str,
    ) -> None:
        """Agrega un evento al historial reciente."""

        with self._lock:
            self._recent_events.append(
                f"{source:<18} {severity}",
            )

    def snapshot(self) -> DashboardData:
        """Obtiene una copia del estado."""

        with self._lock:
            recent_events = list(self._recent_events)

        return DashboardData(
            running=self._state.running,
            events_processed=self._state.events_processed,
            alerts_active=self._state.alerts_active,
            last_source=self._state.last_source or "-",
            last_event_at=self._state.last_event_at,
            recent_events=recent_events,
        )

    def _notify(self) -> None:
        """Notifica a los listeners registrados."""

        with self._lock:
            listeners = tuple(self._listeners)

        data = self.snapshot()

        for listener in listeners:
            listener(data)