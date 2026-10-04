"""Pruebas del EventBus."""

import gc
from datetime import datetime

import pytest

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import HeartbeatEvent


@pytest.mark.asyncio
async def test_subscribe_and_publish() -> None:
    """Un subscriber debe recibir el evento."""

    bus = EventBus()
    received: list[HeartbeatEvent] = []

    async def handler(event: HeartbeatEvent) -> None:
        received.append(event)

    bus.subscribe(HeartbeatEvent, handler)

    event = HeartbeatEvent(
        timestamp=datetime.now(),
    )

    await bus.publish(event)

    assert received == [event]
    assert bus.subscriber_count(HeartbeatEvent) == 1


@pytest.mark.asyncio
async def test_unsubscribe() -> None:
    """Un subscriber eliminado no debe recibir eventos."""

    bus = EventBus()
    received: list[HeartbeatEvent] = []

    async def handler(event: HeartbeatEvent) -> None:
        received.append(event)

    bus.subscribe(HeartbeatEvent, handler)

    bus.unsubscribe(
        HeartbeatEvent,
        handler,
    )

    event = HeartbeatEvent(
        timestamp=datetime.now(),
    )

    await bus.publish(event)

    assert received == []
    assert bus.subscriber_count(HeartbeatEvent) == 0


@pytest.mark.asyncio
async def test_handler_error_does_not_stop_other_handlers() -> None:
    """Un handler defectuoso no debe detener a los demás."""

    bus = EventBus()
    received: list[HeartbeatEvent] = []

    async def failing_handler(event: HeartbeatEvent) -> None:
        raise RuntimeError("error de prueba")

    async def valid_handler(event: HeartbeatEvent) -> None:
        received.append(event)

    bus.subscribe(
        HeartbeatEvent,
        failing_handler,
    )

    bus.subscribe(
        HeartbeatEvent,
        valid_handler,
    )

    await bus.publish(
        HeartbeatEvent(timestamp=datetime.now()),
    )

    assert len(received) == 1


@pytest.mark.asyncio
async def test_dead_subscriber_is_removed() -> None:
    """Las referencias muertas deben limpiarse."""

    bus = EventBus()

    class Subscriber:
        async def handle(self, event: HeartbeatEvent) -> None:
            pass

    subscriber = Subscriber()

    bus.subscribe(
        HeartbeatEvent,
        subscriber.handle,
    )

    assert bus.subscriber_count(HeartbeatEvent) == 1

    del subscriber
    gc.collect()

    await bus.publish(
        HeartbeatEvent(timestamp=datetime.now()),
    )

    assert bus.subscriber_count(HeartbeatEvent) == 0