"""Pruebas del estado central de PulseDesk."""

from pulsedesk.core.state import AppState


def test_state_starts_stopped() -> None:
    """El estado inicial debe estar detenido."""

    state = AppState()

    assert state.running is False
    assert state.events_processed == 0
    assert state.alerts_active == 0
    assert state.last_event_at is None
    assert state.last_source is None


def test_state_can_start() -> None:
    """El estado debe poder marcarse como activo."""

    state = AppState()

    state.set_running(True)

    assert state.running is True


def test_state_can_stop() -> None:
    """El estado debe poder marcarse como detenido."""

    state = AppState(running=True)

    state.set_running(False)

    assert state.running is False


def test_register_event_updates_counter() -> None:
    """Registrar un evento incrementa el contador."""

    state = AppState()

    state.register_event("heartbeat")

    assert state.events_processed == 1
    assert state.last_source == "heartbeat"
    assert state.last_event_at is not None


def test_register_multiple_events() -> None:
    """El contador debe acumular múltiples eventos."""

    state = AppState()

    state.register_event("heartbeat")
    state.register_event("telemetry_file")
    state.register_event("alerts_api")

    assert state.events_processed == 3
    assert state.last_source == "alerts_api"


def test_metadata_is_independent_per_instance() -> None:
    """Cada instancia debe tener su propio diccionario de metadata."""

    first = AppState()
    second = AppState()

    first.metadata["environment"] = "test"

    assert first.metadata["environment"] == "test"
    assert "environment" not in second.metadata
