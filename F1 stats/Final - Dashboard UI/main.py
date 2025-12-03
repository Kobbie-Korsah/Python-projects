"""
Entry point for the PyQt6 F1 Analytics application.
Sets up application-wide resources and launches the main window.
"""

from PyQt6 import QtWidgets

from ui_main import MainWindow


def main() -> None:
    """Bootstrap the Qt event loop and display the main window."""
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
