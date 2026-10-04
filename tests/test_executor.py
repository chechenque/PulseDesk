"""Pruebas del executor de tareas bloqueantes."""

import asyncio
import time

import pytest

from pulsedesk.workers.executor import BlockingExecutor


def slow_operation() -> str:
    """Simula una operación bloqueante."""

    time.sleep(0.1)

    return "OK"


@pytest.mark.asyncio
async def test_blocking_operation_runs_without_blocking_event_loop() -> None:
    """Una operación lenta debe ejecutarse fuera del event loop."""

    executor = BlockingExecutor(max_workers=2)

    try:
        task = asyncio.create_task(
            executor.run(slow_operation),
        )

        await asyncio.sleep(0.01)

        assert not task.done()

        result = await task

        assert result == "OK"

    finally:
        executor.shutdown()