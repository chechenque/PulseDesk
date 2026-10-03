"""Definición de eventos del sistema PulseDesk."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Event:
    """Evento base del sistema."""

    timestamp: datetime


@dataclass(frozen=True, slots=True)
class HeartbeatEvent(Event):
    """Indica que el sistema continúa activo."""

    source: str = "heartbeat"


@dataclass(frozen=True, slots=True)
class TelemetryEvent(Event):
    """Representa un dato de telemetría recibido."""

    source: str
    metric: str
    value: Any


@dataclass(frozen=True, slots=True)
class AlertEvent(Event):
    """Representa una alerta del sistema."""

    source: str
    message: str
    severity: str = "INFO"