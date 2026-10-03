"""Bus de eventos de PulseDesk."""

from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any


EventHandler = Callable[[Any], Awaitable[None]]


class EventBus:
    """Publica eventos y los distribuye a sus suscriptores."""

    def __init__(self) -> None:
        self._subscribers: dict[type[Any], list[EventHandler]] = defaultdict(list)

    def subscribe(
        self,
        event_type: type[Any],
        handler: EventHandler,
    ) -> None:
        """Registra un handler para un tipo de evento."""

        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def unsubscribe(
        self,
        event_type: type[Any],
        handler: EventHandler,
    ) -> None:
        """Elimina un handler previamente registrado."""

        handlers = self._subscribers.get(event_type)

        if handlers is None:
            return

        if handler in handlers:
            handlers.remove(handler)

        if not handlers:
            self._subscribers.pop(event_type, None)

    async def publish(self, event: Any) -> None:
        """Publica un evento a todos sus suscriptores."""

        handlers = tuple(self._subscribers.get(type(event), []))

        for handler in handlers:
            await handler(event)