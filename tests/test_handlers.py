"""Pruebas de los handlers de PulseDesk."""

from datetime import datetime

import pytest

from pulsedesk.core.events import AlertEvent, HeartbeatEvent, TelemetryEvent
from pulsedesk.core.handlers import PulseDeskEventHandlers
from pulsedesk.core.state import AppState
from pulsedesk.ui.bridge import UiBridge


@pytest.fixture
def handlers() -> PulseDeskEventHandlers:
    """Crea los handlers con un estado y bridge reales."""

    state = AppState()
    bridge = UiBridge(state)

    return PulseDeskEventHandlers(
        state=state,
        bridge=bridge,
    )


@pytest.mark.asyncio
async def test_handle_heartbeat(
    handlers: PulseDeskEventHandlers,
) -> None:
    """El handler debe procesar un heartbeat."""

    event = HeartbeatEvent(
        timestamp=datetime.now(),
        source="heartbeat",
    )

    await handlers.handle_heartbeat(event)

    data = handlers._bridge.snapshot()

    assert data.events_processed == 1
    assert data.last_source == "heartbeat"


@pytest.mark.asyncio
async def test_handle_telemetry(
    handlers: PulseDeskEventHandlers,
) -> None:
    """El handler debe procesar telemetría."""

    event = TelemetryEvent(
        timestamp=datetime.now(),
        source="telemetry_file",
        metric="temperature",
        value=25.0,
    )

    await handlers.handle_telemetry(event)

    data = handlers._bridge.snapshot()

    assert data.events_processed == 1
    assert data.last_source == "telemetry_file"


@pytest.mark.asyncio
async def test_handle_alert(
    handlers: PulseDeskEventHandlers,
) -> None:
    """El handler debe procesar una alerta."""

    event = AlertEvent(
        timestamp=datetime.now(),
        source="alerts_api",
        message="Alerta de prueba",
        severity="WARNING",
    )

    await handlers.handle_alert(event)

    data = handlers._bridge.snapshot()

    assert data.events_processed == 1
    assert data.alerts_active == 1
    assert data.last_source == "alerts_api"
