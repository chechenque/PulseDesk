"""Pruebas de la fuente de telemetría basada en archivo."""

import asyncio
from pathlib import Path

import pytest

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import TelemetryEvent
from pulsedesk.sources.telemetry_file import TelemetryFileSource


@pytest.mark.asyncio
async def test_telemetry_file_source_publishes_new_lines(
    tmp_path: Path,
) -> None:
    """La fuente debe publicar las nuevas líneas del archivo."""

    file_path = tmp_path / "telemetry.txt"

    file_path.write_text(
        "temperature=25\nhumidity=60\n",
        encoding="utf-8",
    )

    bus = EventBus()
    received: list[TelemetryEvent] = []

    async def handler(event: TelemetryEvent) -> None:
        received.append(event)

    bus.subscribe(
        TelemetryEvent,
        handler,
    )

    source = TelemetryFileSource(
        event_bus=bus,
        file_path=file_path,
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
    assert len(received) == 2

    assert received[0].value == "temperature=25"
    assert received[1].value == "humidity=60"

    assert all(
        event.source == "telemetry_file"
        for event in received
    )

    assert all(
        event.metric == "message"
        for event in received
    )


@pytest.mark.asyncio
async def test_telemetry_file_source_reads_only_new_lines(
    tmp_path: Path,
) -> None:
    """La fuente no debe publicar nuevamente líneas ya procesadas."""

    file_path = tmp_path / "telemetry.txt"

    file_path.write_text(
        "temperature=25\n",
        encoding="utf-8",
    )

    bus = EventBus()
    received: list[TelemetryEvent] = []

    async def handler(event: TelemetryEvent) -> None:
        received.append(event)

    bus.subscribe(
        TelemetryEvent,
        handler,
    )

    source = TelemetryFileSource(
        event_bus=bus,
        file_path=file_path,
        interval=0.01,
    )

    task = asyncio.create_task(source.start())

    await asyncio.sleep(0.025)

    assert len(received) == 1

    file_path.write_text(
        "temperature=25\nhumidity=60\n",
        encoding="utf-8",
    )

    await asyncio.sleep(0.025)

    await source.stop()

    await asyncio.gather(
        task,
        return_exceptions=True,
    )

    assert len(received) == 2
    assert received[0].value == "temperature=25"
    assert received[1].value == "humidity=60"


@pytest.mark.asyncio
async def test_telemetry_file_source_ignores_empty_lines(
    tmp_path: Path,
) -> None:
    """Las líneas vacías no deben generar eventos."""

    file_path = tmp_path / "telemetry.txt"

    file_path.write_text(
        "\n"
        "temperature=25\n"
        "\n"
        "   \n"
        "humidity=60\n",
        encoding="utf-8",
    )

    bus = EventBus()
    received: list[TelemetryEvent] = []

    async def handler(event: TelemetryEvent) -> None:
        received.append(event)

    bus.subscribe(
        TelemetryEvent,
        handler,
    )

    source = TelemetryFileSource(
        event_bus=bus,
        file_path=file_path,
        interval=0.01,
    )

    task = asyncio.create_task(source.start())

    await asyncio.sleep(0.025)

    await source.stop()

    await asyncio.gather(
        task,
        return_exceptions=True,
    )

    assert len(received) == 2
    assert received[0].value == "temperature=25"
    assert received[1].value == "humidity=60"


@pytest.mark.asyncio
async def test_telemetry_file_source_handles_missing_file(
    tmp_path: Path,
) -> None:
    """Un archivo inexistente no debe producir errores."""

    file_path = tmp_path / "missing.txt"

    bus = EventBus()

    source = TelemetryFileSource(
        event_bus=bus,
        file_path=file_path,
        interval=0.01,
    )

    task = asyncio.create_task(source.start())

    await asyncio.sleep(0.025)

    assert source.running is True

    await source.stop()

    await asyncio.gather(
        task,
        return_exceptions=True,
    )

    assert source.running is False


@pytest.mark.asyncio
async def test_telemetry_file_source_handles_cancellation(
    tmp_path: Path,
) -> None:
    """La fuente debe manejar correctamente una cancelación."""

    file_path = tmp_path / "telemetry.txt"

    file_path.write_text(
        "temperature=25\n",
        encoding="utf-8",
    )

    bus = EventBus()

    source = TelemetryFileSource(
        event_bus=bus,
        file_path=file_path,
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
async def test_telemetry_file_source_stop(
    tmp_path: Path,
) -> None:
    """stop() debe detener la fuente."""

    file_path = tmp_path / "telemetry.txt"

    file_path.write_text(
        "temperature=25\n",
        encoding="utf-8",
    )

    bus = EventBus()

    source = TelemetryFileSource(
        event_bus=bus,
        file_path=file_path,
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