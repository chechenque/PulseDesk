"""Pruebas de la fuente simulada de alertas."""

import asyncio

import pytest

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import AlertEvent
from pulsedesk.sources.alerts_api import AlertsApiSource


@pytest.mark.asyncio
async def test_alerts_api_source_publishes_events() -> None:
    """La fuente debe publicar eventos de alerta."""

    bus = EventBus()
    received: list[AlertEvent] = []

    async def handler(event: AlertEvent) -> None:
        received.append(event)

    bus.subscribe(
        AlertEvent,
        handler,
    )

    source = AlertsApiSource(
        event_bus=bus,
        interval=0.01,
    )

    task = asyncio.create_task(source.start())

    await asyncio.sleep(0.035)

    await source.stop()

    await asyncio.gather(
        task,
        return_exceptions=True,
    )

    assert source.running is False
    assert len(received) >= 1

    for event in received:
        assert isinstance(event, AlertEvent)
        assert event.source == "alerts_api"
        assert event.message == "Alerta de prueba recibida."
        assert event.severity == "WARNING"


@pytest.mark.asyncio
async def test_alerts_api_source_stop() -> None:
    """stop() debe detener la fuente."""

    bus = EventBus()

    source = AlertsApiSource(
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
async def test_alerts_api_source_handles_cancellation() -> None:
    """La fuente debe manejar correctamente una cancelación."""

    bus = EventBus()

    source = AlertsApiSource(
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
async def test_alerts_api_source_uses_custom_interval() -> None:
    """La fuente debe aceptar un intervalo personalizado."""

    bus = EventBus()

    source = AlertsApiSource(
        event_bus=bus,
        interval=0.25,
    )

    assert source.name == "alerts_api"
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