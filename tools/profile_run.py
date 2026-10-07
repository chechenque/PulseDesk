"""Perfilado de una ejecución representativa de PulseDesk."""

from __future__ import annotations

import asyncio
import cProfile
import pstats
import time
from datetime import datetime

from pulsedesk.core.event_bus import EventBus
from pulsedesk.core.events import TelemetryEvent


async def telemetry_handler(event: TelemetryEvent) -> None:
    """Procesa un evento de telemetría."""

    _ = event.metric
    _ = event.value


async def profile_scenario() -> None:
    """Ejecuta un escenario reproducible de procesamiento de eventos."""

    bus = EventBus()

    bus.subscribe(
        TelemetryEvent,
        telemetry_handler,
    )

    for index in range(10_000):
        await bus.publish(
            TelemetryEvent(
                timestamp=datetime.now(),
                source="profile",
                metric="temperature",
                value=index,
            )
        )


def main() -> None:
    """Ejecuta la medición de rendimiento."""

    start = time.perf_counter()

    profiler = cProfile.Profile()
    profiler.enable()

    asyncio.run(profile_scenario())

    profiler.disable()

    elapsed = time.perf_counter() - start

    print()
    print("=" * 60)
    print("PulseDesk RAD - Performance Baseline")
    print("=" * 60)
    print(f"Tiempo total: {elapsed:.6f} segundos")
    print()

    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.print_stats(15)


if __name__ == "__main__":
    main()
