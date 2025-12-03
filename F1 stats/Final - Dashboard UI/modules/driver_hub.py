"""
Driver Hub module leveraging Jolpica metadata and FastF1 session stats.
"""

from typing import Dict, Optional

import pandas as pd
from PyQt6 import QtWidgets

from core.threading import run_in_thread
from utils import api_utils, fastf1_utils
from utils.ui_helpers import labeled_value


class DriverHubModule(QtWidgets.QWidget):
    """Displays driver profile, constructor history, and season performance."""

    def __init__(self) -> None:
        super().__init__()
        self._worker = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.driver_id = QtWidgets.QLineEdit()
        self.driver_id.setPlaceholderText("e.g., max_verstappen")
        self.api_key = QtWidgets.QLineEdit()
        self.api_key.setPlaceholderText("Jolpica API key (optional)")
        self.season = QtWidgets.QSpinBox()
        self.season.setRange(1950, 2050)
        self.season.setValue(2023)
        form.addRow("Driver ID", self.driver_id)
        form.addRow("API Key", self.api_key)
        form.addRow("Season", self.season)
        layout.addLayout(form)

        btn = QtWidgets.QPushButton("Load Driver Hub")
        btn.clicked.connect(self._start_load)
        layout.addWidget(btn)

        self.profile_box = QtWidgets.QGroupBox("Driver Profile")
        self.profile_layout = QtWidgets.QHBoxLayout(self.profile_box)
        layout.addWidget(self.profile_box)

        self.performance_table = QtWidgets.QTableWidget(0, 2)
        self.performance_table.setHorizontalHeaderLabels(["Metric", "Value"])
        layout.addWidget(self.performance_table)

        self.status = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status)

    def _start_load(self) -> None:
        driver_id = self.driver_id.text().strip()
        if not driver_id:
            self.status.setText("Enter a driver ID.")
            return
        self.status.setText("Fetching driver data...")
        self._worker = run_in_thread(
            self._load_data,
            on_result=self._handle_result,
            on_error=self._handle_error,
            driver_id=driver_id,
            api_key=self.api_key.text().strip() or None,
            season=self.season.value(),
        )

    @staticmethod
    def _load_data(driver_id: str, api_key: Optional[str], season: int) -> Dict:
        profile = api_utils.fetch_driver_profile(driver_id, api_key)
        stats = api_utils.fetch_driver_stats(driver_id, api_key)
        session = fastf1_utils.load_session(season, 1, "Q")
        quali_avg = None
        if session:
            laps = fastf1_utils.get_laps(session)
            lap_times = laps.pick_driver(driver_id[:3].upper())["LapTime"]
            quali_avg = lap_times.mean() if not lap_times.empty else None
        return {"profile": profile, "stats": stats, "quali_avg": quali_avg}

    def _handle_result(self, data: Dict) -> None:
        for i in reversed(range(self.profile_layout.count())):
            item = self.profile_layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()

        profile = data.get("profile", {})
        stats = data.get("stats", {})
        self.profile_layout.addWidget(labeled_value("Name", str(profile.get("givenName", "N/A"))))
        self.profile_layout.addWidget(labeled_value("Number", str(profile.get("permanentNumber", "N/A"))))
        self.profile_layout.addWidget(labeled_value("Nationality", str(profile.get("nationality", "N/A"))))
        self.profile_layout.addWidget(labeled_value("Code", str(profile.get("code", "N/A"))))

        metrics = {
            "Championships": stats.get("championships"),
            "Wins": stats.get("wins"),
            "Podiums": stats.get("podiums"),
            "Poles": stats.get("poles"),
            "Fastest Laps": stats.get("fastestLaps"),
            "Avg Quali (Round1)": data.get("quali_avg"),
        }
        self.performance_table.setRowCount(0)
        for i, (metric, value) in enumerate(metrics.items()):
            self.performance_table.insertRow(i)
            self.performance_table.setItem(i, 0, QtWidgets.QTableWidgetItem(metric))
            self.performance_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(value)))

        self.status.setText("Driver hub loaded.")

    def _handle_error(self, exc: Exception) -> None:
        self.status.setText(f"Error: {exc}")
