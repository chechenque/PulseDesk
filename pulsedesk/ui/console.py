"""Interfaz temporal de consola para PulseDesk."""

from pulsedesk.ui.model import DashboardData


class ConsoleDashboard:
    """Dashboard temporal para validar la arquitectura."""

    def __init__(self) -> None:
        self._last_events = 0

    def update(self, data: DashboardData) -> None:
        """Actualiza el dashboard."""

        if data.events_processed == self._last_events:
            return

        self._last_events = data.events_processed

        status = "ACTIVO" if data.running else "DETENIDO"

        print(
            "\n"
            "╔══════════════════════════════════════╗\n"
            "║          PULSEDESK RAD               ║\n"
            "╠══════════════════════════════════════╣\n"
            f"║ Estado:             {status:<16}║\n"
            f"║ Eventos procesados: {data.events_processed:<16}║\n"
            f"║ Alertas activas:    {data.alerts_active:<16}║\n"
            f"║ Última fuente:      {data.last_source:<16}║\n"
            "╚══════════════════════════════════════╝"
        )