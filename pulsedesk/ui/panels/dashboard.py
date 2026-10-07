"""Panel principal del dashboard."""

from pulsedesk.ui.model import DashboardData


class DashboardPanel:
    """Representa conceptualmente el dashboard."""

    def __init__(self) -> None:
        self._data = DashboardData()

    def update(self, data: DashboardData) -> None:
        """Actualiza los datos mostrados."""

        self._data = data

    @property
    def data(self) -> DashboardData:
        """Devuelve los datos actuales."""

        return self._data
