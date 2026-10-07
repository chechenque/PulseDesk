"""Modelo de datos utilizado por la interfaz de PulseDesk."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class DashboardData:
    """Datos resumidos para el dashboard."""

    running: bool = False
    events_processed: int = 0
    alerts_active: int = 0
    last_source: str = "-"
    last_event_at: datetime | None = None
    recent_events: list[str] = field(default_factory=list)
