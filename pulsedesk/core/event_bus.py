"""Bus de eventos de PulseDesk."""

from __future__ import annotations

import inspect
import logging
import weakref
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any


logger = logging.getLogger(__name__)

EventHandler = Callable[[Any], Awaitable[None]]


class EventBus:
    """Distribuye eventos a sus suscriptores."""

    def __init__(self) -> None:
        self._subscribers: dict[
            type[Any],
            list[weakref.ReferenceType[Any]],
        ] = defaultdict(list)

    def subscribe(
        self,
        event_type: type[Any],
        handler: EventHandler,
    ) -> None:
        """Registra un handler utilizando una referencia débil."""

        reference: weakref.ReferenceType[Any]

        if inspect.ismethod(handler):
            reference = weakref.WeakMethod(handler)
        else:
            reference = weakref.ref(handler)

        self._subscribers[event_type].append(reference)

    def unsubscribe(
        self,
        event_type: type[Any],
        handler: EventHandler,
    ) -> None:
        """Elimina un handler."""

        references = self._subscribers.get(event_type)

        if references is None:
            return

        references[:] = [
            reference
            for reference in references
            if reference() is not handler and reference() is not None
        ]

        if not references:
            self._subscribers.pop(event_type, None)

    async def publish(self, event: Any) -> None:
        """Publica un evento a sus suscriptores."""

        references = self._subscribers.get(type(event))

        if not references:
            return

        dead_found = False

        for reference in references:
            handler = reference()

            if handler is None:
                dead_found = True
                continue

            try:
                result = handler(event)
                await result

            except Exception:
                logger.exception(
                    "Error procesando evento %s con %r",
                    type(event).__name__,
                    handler,
                )

        if dead_found:
            self._subscribers[type(event)] = [
                reference
                for reference in references
                if reference() is not None
            ]

    def subscriber_count(
        self,
        event_type: type[Any],
    ) -> int:
        """Devuelve el número de suscriptores activos."""

        references = self._subscribers.get(event_type, [])

        alive = [
            reference
            for reference in references
            if reference() is not None
        ]

        self._subscribers[event_type] = alive

        return len(alive)