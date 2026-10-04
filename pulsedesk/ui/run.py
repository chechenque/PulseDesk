"""Punto de entrada de la interfaz gráfica."""

from pulsedesk.ui.app import DashboardWindow, create_app


def main() -> None:
    """Inicia la interfaz gráfica."""

    app = create_app()

    window = DashboardWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()