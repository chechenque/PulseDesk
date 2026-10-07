"""Pruebas del ciclo principal de PulseDesk."""

import asyncio

import pytest

from pulsedesk.core.loop import PulseDeskLoop
from pulsedesk.sources.base import EventSource


class FakeSource(EventSource):
    """Fuente simulada para probar el ciclo principal."""

    def __init__(self, name: str = "fake") -> None:
        super().__init__(name)
        self.start_count = 0
        self.stop_count = 0

    async def start(self) -> None:
        """Simula una fuente activa."""

        self.start_count += 1
        self._running = True

        try:
            while self._running:
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            raise
        finally:
            self._running = False

    async def stop(self) -> None:
        """Detiene la fuente simulada."""

        if self._running:
            self.stop_count += 1

        self._running = False


@pytest.mark.asyncio
async def test_loop_starts_sources() -> None:
    """El loop debe iniciar las fuentes."""

    source = FakeSource()
    loop = PulseDeskLoop([source])

    task = asyncio.create_task(loop.start())

    await asyncio.sleep(0.03)

    assert source.start_count == 1
    assert source.running is True

    await loop.stop()

    result = await asyncio.gather(
        task,
        return_exceptions=True,
    )

    assert isinstance(result[0], asyncio.CancelledError)


@pytest.mark.asyncio
async def test_loop_stops_sources() -> None:
    """El loop debe detener todas las fuentes."""

    source = FakeSource()
    loop = PulseDeskLoop([source])

    task = asyncio.create_task(loop.start())

    await asyncio.sleep(0.02)

    await loop.stop()

    result = await asyncio.gather(
        task,
        return_exceptions=True,
    )

    assert isinstance(result[0], asyncio.CancelledError)
    assert source.stop_count == 1
    assert source.running is False


@pytest.mark.asyncio
async def test_loop_does_not_start_twice() -> None:
    """Una segunda llamada a start no debe iniciar otra ejecución."""

    source = FakeSource()
    loop = PulseDeskLoop([source])

    task = asyncio.create_task(loop.start())

    await asyncio.sleep(0.02)

    await loop.start()

    assert source.start_count == 1

    await loop.stop()

    result = await asyncio.gather(
        task,
        return_exceptions=True,
    )

    assert isinstance(result[0], asyncio.CancelledError)


@pytest.mark.asyncio
async def test_loop_handles_external_cancellation() -> None:
    """Una cancelación externa debe limpiar correctamente el loop."""

    source = FakeSource()
    loop = PulseDeskLoop([source])

    task = asyncio.create_task(loop.start())

    await asyncio.sleep(0.02)

    assert source.running is True

    task.cancel()

    result = await asyncio.gather(
        task,
        return_exceptions=True,
    )

    assert isinstance(result[0], asyncio.CancelledError)

    # La cancelación externa también cancela la tarea de la fuente.
    # El finally de FakeSource debe dejarla detenida.
    assert source.running is False


@pytest.mark.asyncio
async def test_loop_stop_when_already_stopped() -> None:
    """Detener un loop que no inició no debe producir errores."""

    source = FakeSource()
    loop = PulseDeskLoop([source])

    await loop.stop()

    assert source.stop_count == 0


@pytest.mark.asyncio
async def test_loop_cleans_up_after_source_failure() -> None:
    """El loop debe ejecutar la limpieza si una fuente falla."""

    class FailingSource(EventSource):
        """Fuente que falla deliberadamente."""

        def __init__(self) -> None:
            super().__init__("failing")
            self.stop_count = 0

        async def start(self) -> None:
            """Provoca un error controlado."""

            self._running = True
            raise RuntimeError("error de prueba")

        async def stop(self) -> None:
            """Registra la limpieza."""

            if self._running:
                self.stop_count += 1

            self._running = False

    source = FailingSource()
    loop = PulseDeskLoop([source])

    with pytest.raises(RuntimeError, match="error de prueba"):
        await loop.start()

    assert source.stop_count == 1
    assert source.running is False