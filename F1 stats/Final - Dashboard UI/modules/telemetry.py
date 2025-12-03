"""
Telemetry viewer module with speed/throttle traces and overlaid comparisons.
"""

from typing import Optional

from PyQt6 import QtCore, QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from core.threading import run_in_thread
from utils import fastf1_utils, plot_utils


class TelemetryModule(QtWidgets.QWidget):
    """Displays telemetry plots for selected drivers and sessions."""

    def __init__(self) -> None:
        super().__init__()
        self._worker = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)

        controls = QtWidgets.QHBoxLayout()
        self.season_input = QtWidgets.QSpinBox()
        self.season_input.setRange(1950, 2050)
        self.season_input.setValue(2023)
        self.round_input = QtWidgets.QSpinBox()
        self.round_input.setRange(1, 25)
        self.round_input.setValue(1)
        self.session_input = QtWidgets.QComboBox()
        self.session_input.addItems(["R", "Q", "FP1", "FP2", "FP3", "S"])
        self.driver_input = QtWidgets.QLineEdit()
        self.driver_input.setPlaceholderText("Driver code (e.g., VER)")
        fetch_btn = QtWidgets.QPushButton("Load Telemetry")
        fetch_btn.clicked.connect(self._start_fetch)

        for widget in (
            QtWidgets.QLabel("Season"),
            self.season_input,
            QtWidgets.QLabel("Round"),
            self.round_input,
            QtWidgets.QLabel("Session"),
            self.session_input,
            QtWidgets.QLabel("Driver"),
            self.driver_input,
            fetch_btn,
        ):
            controls.addWidget(widget)

        layout.addLayout(controls)

        self.figure = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.status = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status)

    def _start_fetch(self) -> None:
        """Kick off telemetry load in a background thread."""
        season = self.season_input.value()
        round_no = self.round_input.value()
        session_name = self.session_input.currentText()
        driver = self.driver_input.text().strip().upper()

        if not driver:
            self.status.setText("Enter a driver code.")
            return

        self.status.setText("Loading telemetry...")
        self._worker = run_in_thread(
            self._load_data,
            on_result=self._handle_result,
            on_error=self._handle_error,
            season=season,
            round_no=round_no,
            session_name=session_name,
            driver=driver,
        )

    @staticmethod
    def _load_data(season: int, round_no: int, session_name: str, driver: str) -> Optional[object]:
        session = fastf1_utils.load_session(season, round_no, session_name)
        if not session:
            raise RuntimeError("Unable to load session")
        telemetry = fastf1_utils.build_driver_telemetry(session, driver)
        return telemetry

    def _handle_result(self, telemetry) -> None:  # type: ignore[override]
        """Render plot on successful telemetry fetch."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        plot_utils.plot_speed_trace(telemetry, ax=ax)
        self.canvas.draw()
        self.status.setText("Telemetry loaded.")

    def _handle_error(self, exc: Exception) -> None:
        self.status.setText(f"Error: {exc}")
