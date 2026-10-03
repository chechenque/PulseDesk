"""Estado central de PulseDesk."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AppState:
    """Representa el estado actual de la aplicación."""

    running: bool = False
    events_processed: int = 0
    alerts_active: int = 0
    last_event_at: datetime | None = None
    last_source: str | None = None

    metadata: dict[str, str] = field(default_factory=dict)

    def register_event(self, source: str) -> None:
        """Registra que se recibió un evento."""

        self.events_processed += 1
        self.last_event_at = datetime.now()
        self.last_source = source

    def set_running(self, running: bool) -> None:
        """Actualiza el estado de ejecución."""

        self.running = running