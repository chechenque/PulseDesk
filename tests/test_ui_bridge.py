"""Pruebas del UiBridge."""

from datetime import datetime

from pulsedesk.core.events import AlertEvent, HeartbeatEvent, TelemetryEvent
from pulsedesk.core.state import AppState
from pulsedesk.ui.bridge import UiBridge


def test_snapshot_returns_initial_state() -> None:
    """El snapshot inicial debe representar el estado por defecto."""

    state = AppState()
    bridge = UiBridge(state)

    data = bridge.snapshot()

    assert data.running is False
    assert data.events_processed == 0
    assert data.alerts_active == 0
    assert data.last_source == "-"
    assert data.last_event_at is None
    assert data.recent_events == []


def test_heartbeat_updates_dashboard() -> None:
    """Un heartbeat debe actualizar los datos del dashboard."""

    state = AppState()
    bridge = UiBridge(state)

    bridge.handle_heartbeat(
        HeartbeatEvent(
            timestamp=datetime.now(),
            source="heartbeat",
        )
    )

    data = bridge.snapshot()

    assert data.events_processed == 1
    assert data.last_source == "heartbeat"
    assert data.last_event_at is not None
    assert len(data.recent_events) == 1
    assert "heartbeat" in data.recent_events[0]
    assert "INFO" in data.recent_events[0]


def test_telemetry_updates_dashboard() -> None:
    """La telemetría debe actualizar los datos del dashboard."""

    state = AppState()
    bridge = UiBridge(state)

    bridge.handle_telemetry(
        TelemetryEvent(
            timestamp=datetime.now(),
            source="telemetry_file",
            metric="temperature",
            value=24.5,
        )
    )

    data = bridge.snapshot()

    assert data.events_processed == 1
    assert data.last_source == "telemetry_file"
    assert len(data.recent_events) == 1
    assert "telemetry_file" in data.recent_events[0]


def test_alert_increments_active_alerts() -> None:
    """Una alerta debe incrementar el contador de alertas."""

    state = AppState()
    bridge = UiBridge(state)

    bridge.handle_alert(
        AlertEvent(
            timestamp=datetime.now(),
            source="alerts_api",
            message="Test alert",
            severity="WARNING",
        )
    )

    data = bridge.snapshot()

    assert data.events_processed == 1
    assert data.alerts_active == 1
    assert data.last_source == "alerts_api"
    assert len(data.recent_events) == 1
    assert "alerts_api" in data.recent_events[0]
    assert "WARNING" in data.recent_events[0]


def test_listener_receives_dashboard_data() -> None:
    """Los listeners deben recibir actualizaciones."""

    state = AppState()
    bridge = UiBridge(state)

    received = []

    def listener(data) -> None:
        received.append(data)

    bridge.add_listener(listener)

    bridge.handle_heartbeat(
        HeartbeatEvent(
            timestamp=datetime.now(),
        )
    )

    assert len(received) == 1
    assert received[0].events_processed == 1


def test_removed_listener_stops_receiving_updates() -> None:
    """Un listener eliminado no debe recibir nuevas actualizaciones."""

    state = AppState()
    bridge = UiBridge(state)

    received = []

    def listener(data) -> None:
        received.append(data)

    bridge.add_listener(listener)
    bridge.remove_listener(listener)

    bridge.handle_heartbeat(
        HeartbeatEvent(
            timestamp=datetime.now(),
        )
    )

    assert received == []


def test_recent_events_are_recorded() -> None:
    """El historial debe conservar los eventos recibidos."""

    state = AppState()
    bridge = UiBridge(state)

    bridge.handle_heartbeat(
        HeartbeatEvent(
            timestamp=datetime.now(),
            source="heartbeat",
        )
    )

    bridge.handle_telemetry(
        TelemetryEvent(
            timestamp=datetime.now(),
            source="telemetry_file",
            metric="temperature",
            value=25.0,
        )
    )

    data = bridge.snapshot()

    assert len(data.recent_events) == 2
    assert "heartbeat" in data.recent_events[0]
    assert "telemetry_file" in data.recent_events[1]


def test_recent_events_keep_only_last_ten() -> None:
    """El historial debe limitarse a los últimos diez eventos."""

    state = AppState()
    bridge = UiBridge(state)

    for index in range(15):
        bridge.handle_heartbeat(
            HeartbeatEvent(
                timestamp=datetime.now(),
                source=f"heartbeat-{index}",
            )
        )

    data = bridge.snapshot()

    assert len(data.recent_events) == 10
    assert "heartbeat-5" in data.recent_events[0]
    assert "heartbeat-14" in data.recent_events[-1]
