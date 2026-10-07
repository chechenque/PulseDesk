"""Pruebas de la arquitectura Pub/Sub de PulseDesk."""

import asyncio

import pytest

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import TelemetryEvent
from pulsedesk.sources.system_status import SystemStatusSource


@pytest.mark.asyncio
async def test_system_status_source_publishes_events() -> None:
    """La fuente debe publicar eventos sin depender de la UI."""

    bus = EventBus()
    received: list[TelemetryEvent] = []

    async def handler(event: TelemetryEvent) -> None:
        received.append(event)

    bus.subscribe(
        TelemetryEvent,
        handler,
    )

    source = SystemStatusSource(
        event_bus=bus,
        interval=0.01,
    )

    task = asyncio.create_task(
        source.start(),
    )

    await asyncio.sleep(0.03)

    await source.stop()

    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

    assert len(received) >= 1
    assert received[0].source == "system_status"
    assert received[0].metric == "status"
    assert received[0].value == "OK"
