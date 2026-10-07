"""Ejecución de tareas bloqueantes fuera del event loop."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar

T = TypeVar("T")


class BlockingExecutor:
    """Ejecuta operaciones bloqueantes en un pool de hilos."""

    def __init__(self, max_workers: int = 4) -> None:
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="pulsedesk-worker",
        )

    async def run(
        self,
        function: Callable[..., T],
        *args: object,
    ) -> T:
        """Ejecuta una función bloqueante fuera del event loop."""

        loop = asyncio.get_running_loop()

        return await loop.run_in_executor(
            self._executor,
            function,
            *args,
        )

    def shutdown(self) -> None:
        """Libera los recursos del executor."""

        self._executor.shutdown(
            wait=True,
            cancel_futures=True,
        )
