"""Aplicación gráfica de PulseDesk."""

from __future__ import annotations

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from pulsedesk.ui.model import DashboardData


class DashboardWindow(QMainWindow):
    """Ventana principal del dashboard."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("PulseDesk RAD")
        self.resize(1100, 700)

        self._build_ui()

    def _build_ui(self) -> None:
        """Construye la interfaz."""

        central = QWidget()
        layout = QVBoxLayout(central)

        title = QLabel("PulseDesk RAD")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel(
            "Centro de Control de Eventos en Tiempo Real",
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        metrics = QGridLayout()

        self._status_value = QLabel("DETENIDO")
        self._events_value = QLabel("0")
        self._alerts_value = QLabel("0")
        self._source_value = QLabel("-")

        metrics.addWidget(QLabel("Estado"), 0, 0)
        metrics.addWidget(self._status_value, 0, 1)

        metrics.addWidget(QLabel("Eventos procesados"), 1, 0)
        metrics.addWidget(self._events_value, 1, 1)

        metrics.addWidget(QLabel("Alertas activas"), 2, 0)
        metrics.addWidget(self._alerts_value, 2, 1)

        metrics.addWidget(QLabel("Última fuente"), 3, 0)
        metrics.addWidget(self._source_value, 3, 1)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(metrics)

        self.setCentralWidget(central)

    def update_dashboard(self, data: DashboardData) -> None:
        """Actualiza las métricas del dashboard."""

        self._status_value.setText(
            "ACTIVO" if data.running else "DETENIDO",
        )

        self._events_value.setText(
            str(data.events_processed),
        )

        self._alerts_value.setText(
            str(data.alerts_active),
        )

        self._source_value.setText(
            data.last_source,
        )