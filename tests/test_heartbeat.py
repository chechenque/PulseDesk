"""Pruebas de la fuente heartbeat de PulseDesk."""

import asyncio

import pytest

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import HeartbeatEvent
from pulsedesk.sources.heartbeat import HeartbeatSource


@pytest.mark.asyncio
async def test_heartbeat_source_publishes_events() -> None:
    """La fuente debe publicar eventos heartbeat."""

    bus = EventBus()
    received: list[HeartbeatEvent] = []

    async def handler(event: HeartbeatEvent) -> None:
        received.append(event)

    bus.subscribe(
        HeartbeatEvent,
        handler,
    )

    source = HeartbeatSource(
        event_bus=bus,
        interval=0.01,
    )

    task = asyncio.create_task(source.start())

    await asyncio.sleep(0.035)

    await source.stop()

    task.cancel()

    await asyncio.gather(
        task,
        return_exceptions=True,
    )

    assert source.running is False
    assert len(received) >= 1

    for event in received:
        assert isinstance(event, HeartbeatEvent)
        assert event.source == "heartbeat"


@pytest.mark.asyncio
async def test_heartbeat_source_stop() -> None:
    """stop() debe detener la fuente."""

    bus = EventBus()

    source = HeartbeatSource(
        event_bus=bus,
        interval=0.01,
    )

    task = asyncio.create_task(source.start())

    await asyncio.sleep(0.02)

    assert source.running is True

    await source.stop()

    await asyncio.gather(
        task,
        return_exceptions=True,
    )

    assert source.running is False


@pytest.mark.asyncio
async def test_heartbeat_source_handles_cancellation() -> None:
    """La fuente debe manejar correctamente una cancelación."""

    bus = EventBus()

    source = HeartbeatSource(
        event_bus=bus,
        interval=0.1,
    )

    task = asyncio.create_task(source.start())

    await asyncio.sleep(0.01)

    assert source.running is True

    task.cancel()

    result = await asyncio.gather(
        task,
        return_exceptions=True,
    )

    assert isinstance(result[0], asyncio.CancelledError)
    assert source.running is False


@pytest.mark.asyncio
async def test_heartbeat_source_uses_custom_interval() -> None:
    """La fuente debe aceptar un intervalo personalizado."""

    bus = EventBus()

    source = HeartbeatSource(
        event_bus=bus,
        interval=0.25,
    )

    assert source.name == "heartbeat"
    assert source.running is False

    task = asyncio.create_task(source.start())

    await asyncio.sleep(0.01)

    assert source.running is True

    await source.stop()

    await asyncio.gather(
        task,
        return_exceptions=True,
    )

    assert source.running is False