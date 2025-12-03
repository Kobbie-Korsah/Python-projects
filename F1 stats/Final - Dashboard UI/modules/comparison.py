"""
Comparison module for Driver vs Driver and Team vs Team metrics.
"""

import pandas as pd
from PyQt6 import QtWidgets

from core.threading import run_in_thread
from utils import fastf1_utils


class ComparisonModule(QtWidgets.QWidget):
    """Allows comparing two drivers or teams using lap statistics."""

    def __init__(self) -> None:
        super().__init__()
        self._worker = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.season = QtWidgets.QSpinBox()
        self.season.setRange(1950, 2050)
        self.season.setValue(2023)
        self.round_no = QtWidgets.QSpinBox()
        self.round_no.setRange(1, 25)
        self.round_no.setValue(1)
        self.driver_a = QtWidgets.QLineEdit()
        self.driver_a.setPlaceholderText("Driver A code")
        self.driver_b = QtWidgets.QLineEdit()
        self.driver_b.setPlaceholderText("Driver B code")
        form.addRow("Season", self.season)
        form.addRow("Round", self.round_no)
        form.addRow("Driver A", self.driver_a)
        form.addRow("Driver B", self.driver_b)
        layout.addLayout(form)

        btn = QtWidgets.QPushButton("Compare Drivers")
        btn.clicked.connect(self._start_compare)
        layout.addWidget(btn)

        self.result_table = QtWidgets.QTableWidget(0, 3)
        self.result_table.setHorizontalHeaderLabels(["Metric", "Driver A", "Driver B"])
        layout.addWidget(self.result_table)

        self.status = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status)

    def _start_compare(self) -> None:
        driver_a = self.driver_a.text().strip().upper()
        driver_b = self.driver_b.text().strip().upper()
        if not driver_a or not driver_b:
            self.status.setText("Enter both driver codes.")
            return
        self.status.setText("Running comparison...")
        self._worker = run_in_thread(
            self._compare,
            on_result=self._handle_result,
            on_error=self._handle_error,
            season=self.season.value(),
            round_no=self.round_no.value(),
            driver_a=driver_a,
            driver_b=driver_b,
        )

    @staticmethod
    def _compare(season: int, round_no: int, driver_a: str, driver_b: str) -> pd.DataFrame:
        session = fastf1_utils.load_session(season, round_no, "R")
        if not session:
            raise RuntimeError("Failed to load session")
        laps = fastf1_utils.get_laps(session)
        stats = []
        for driver in (driver_a, driver_b):
            driver_laps = laps.pick_driver(driver)
            stats.append(
                {
                    "Driver": driver,
                    "AvgLap": driver_laps["LapTime"].mean(),
                    "BestLap": driver_laps["LapTime"].min(),
                    "StdDev": driver_laps["LapTime"].std(),
                }
            )
        return pd.DataFrame(stats)

    def _handle_result(self, df: pd.DataFrame) -> None:
        self.result_table.setRowCount(0)
        metrics = ["AvgLap", "BestLap", "StdDev"]
        for i, metric in enumerate(metrics):
            self.result_table.insertRow(i)
            self.result_table.setItem(i, 0, QtWidgets.QTableWidgetItem(metric))
            self.result_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(df.iloc[0][metric])))
            self.result_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(df.iloc[1][metric])))
        self.status.setText("Comparison complete.")

    def _handle_error(self, exc: Exception) -> None:
        self.status.setText(f"Error: {exc}")
