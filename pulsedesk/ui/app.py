"""Aplicación gráfica de PulseDesk."""

from __future__ import annotations

import sys
from typing import cast

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QGroupBox,
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

        self.setWindowTitle("PulseDesk RAD · Centro de Control")
        self.resize(1100, 700)

        self._build_ui()

    def _build_ui(self) -> None:
        """Construye la interfaz."""

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setSpacing(18)

        # Encabezado
        title = QLabel("PulseDesk RAD")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel(
            "Centro de Control de Eventos en Tiempo Real",
        )
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Métricas principales
        metrics = QGridLayout()
        metrics.setSpacing(15)

        status_card, self._status_value = self._create_metric_card(
            "Estado del sistema",
            "DETENIDO",
        )

        events_card, self._events_value = self._create_metric_card(
            "Eventos procesados",
            "0",
        )

        alerts_card, self._alerts_value = self._create_metric_card(
            "Alertas activas",
            "0",
        )

        source_card, self._source_value = self._create_metric_card(
            "Última fuente",
            "-",
        )

        metrics.addWidget(status_card, 0, 0)
        metrics.addWidget(events_card, 0, 1)
        metrics.addWidget(alerts_card, 1, 0)
        metrics.addWidget(source_card, 1, 1)

        layout.addLayout(metrics)

        # Actividad reciente
        event_group = QGroupBox("Actividad reciente")
        event_layout = QVBoxLayout(event_group)

        self._event_time_value = QLabel("-")
        self._event_time_value.setObjectName("eventInfo")

        event_layout.addWidget(
            self._event_time_value,
        )

        self._recent_events = QLabel("Sin eventos recibidos")
        self._recent_events.setObjectName("recentEvents")
        self._recent_events.setWordWrap(True)

        event_layout.addWidget(
            self._recent_events,
        )

        layout.addWidget(event_group)

        layout.addStretch()

        self.setCentralWidget(central)

        self._apply_styles()

    def _create_metric_card(
        self,
        title: str,
        value: str,
    ) -> tuple[QGroupBox, QLabel]:
        """Crea una tarjeta de métrica."""

        card = QGroupBox()
        card.setObjectName("metricCard")

        layout = QVBoxLayout(card)

        title_label = QLabel(title)
        title_label.setObjectName("metricTitle")

        value_label = QLabel(value)
        value_label.setObjectName("metricValue")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return card, value_label

    def _apply_styles(self) -> None:
        """Aplica estilos visuales al dashboard."""

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f4f6f8;
                color: #1f2937;
            }

            QWidget {
                color: #1f2937;
            }

            QLabel#title {
                color: #111827;
                font-size: 30px;
                font-weight: bold;
            }

            QLabel#subtitle {
                color: #4b5563;
                font-size: 15px;
                margin-bottom: 10px;
            }

            QGroupBox#metricCard {
                background-color: #ffffff;
                color: #1f2937;
                border: 1px solid #d9dee3;
                border-radius: 10px;
                padding: 12px;
            }

            QLabel#metricTitle {
                color: #6b7280;
                font-size: 13px;
            }

            QLabel#metricValue {
                color: #111827;
                font-size: 25px;
                font-weight: bold;
                padding: 8px;
            }

            QGroupBox {
                background-color: #ffffff;
                color: #1f2937;
                font-weight: bold;
                border: 1px solid #d9dee3;
                border-radius: 10px;
                margin-top: 10px;
                padding: 15px;
            }

            QLabel#eventInfo {
                color: #374151;
                font-size: 14px;
                padding: 10px;
            }

            QLabel#recentEvents {
                color: #374151;
                font-size: 13px;
                padding: 8px;
                font-family: monospace;
            }
            """,
        )

    def update_dashboard(self, data: DashboardData) -> None:
        """Actualiza las métricas del dashboard."""

        status = "ACTIVO" if data.running else "DETENIDO"

        self._status_value.setText(status)
        self._events_value.setText(
            str(data.events_processed),
        )
        self._alerts_value.setText(
            str(data.alerts_active),
        )
        self._source_value.setText(
            data.last_source,
        )

        if data.last_event_at is None:
            self._event_time_value.setText(
                "Sin eventos recibidos",
            )
        else:
            self._event_time_value.setText(
                data.last_event_at.strftime(
                    "Último evento: %Y-%m-%d %H:%M:%S",
                ),
            )

        if data.recent_events:
            self._recent_events.setText(
                "\n".join(f"• {event}" for event in reversed(data.recent_events)),
            )
        else:
            self._recent_events.setText(
                "Sin eventos recibidos",
            )


def create_app() -> QApplication:
    """Crea la aplicación Qt."""

    instance = QApplication.instance()

    if instance is not None:
        return cast(QApplication, instance)

    return QApplication(sys.argv)
