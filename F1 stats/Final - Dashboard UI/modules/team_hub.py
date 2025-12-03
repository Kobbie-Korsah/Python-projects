"""
Team Hub module for constructor-level insights and driver pairing stats.
"""

from typing import Dict, Optional

import pandas as pd
from PyQt6 import QtWidgets

from core.threading import run_in_thread
from utils import api_utils, fastf1_utils


class TeamHubModule(QtWidgets.QWidget):
    """Displays team profile and strategy metrics."""

    def __init__(self) -> None:
        super().__init__()
        self._worker = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.constructor_id = QtWidgets.QLineEdit()
        self.constructor_id.setPlaceholderText("e.g., red_bull")
        self.api_key = QtWidgets.QLineEdit()
        self.api_key.setPlaceholderText("Jolpica API key (optional)")
        self.season = QtWidgets.QSpinBox()
        self.season.setRange(1950, 2050)
        self.season.setValue(2023)
        self.round_no = QtWidgets.QSpinBox()
        self.round_no.setRange(1, 25)
        self.round_no.setValue(1)
        form.addRow("Constructor ID", self.constructor_id)
        form.addRow("API Key", self.api_key)
        form.addRow("Season", self.season)
        form.addRow("Round", self.round_no)
        layout.addLayout(form)

        btn = QtWidgets.QPushButton("Load Team Hub")
        btn.clicked.connect(self._start_load)
        layout.addWidget(btn)

        self.profile_table = QtWidgets.QTableWidget(0, 2)
        self.profile_table.setHorizontalHeaderLabels(["Field", "Value"])
        layout.addWidget(self.profile_table)

        self.strategy_table = QtWidgets.QTableWidget(0, 2)
        self.strategy_table.setHorizontalHeaderLabels(["Strategy Metric", "Value"])
        layout.addWidget(self.strategy_table)

        self.status = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status)

    def _start_load(self) -> None:
        constructor_id = self.constructor_id.text().strip()
        if not constructor_id:
            self.status.setText("Enter a constructor ID.")
            return
        self.status.setText("Loading team data...")
        self._worker = run_in_thread(
            self._load_data,
            on_result=self._handle_result,
            on_error=self._handle_error,
            constructor_id=constructor_id,
            api_key=self.api_key.text().strip() or None,
            season=self.season.value(),
            round_no=self.round_no.value(),
        )

    @staticmethod
    def _load_data(constructor_id: str, api_key: Optional[str], season: int, round_no: int) -> Dict:
        profile = api_utils.fetch_constructor(constructor_id, api_key)
        session = fastf1_utils.load_session(season, round_no, "R")
        pit_stats = None
        if session:
            pit_stats = fastf1_utils.pit_stop_summary(session)
        return {"profile": profile, "pit_stats": pit_stats}

    def _handle_result(self, data: Dict) -> None:
        profile = data.get("profile", {})
        self.profile_table.setRowCount(0)
        for i, (k, v) in enumerate(profile.items()):
            self.profile_table.insertRow(i)
            self.profile_table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(k)))
            self.profile_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(v)))

        pit_stats: Optional[pd.DataFrame] = data.get("pit_stats")
        self.strategy_table.setRowCount(0)
        if pit_stats is not None and not pit_stats.empty:
            for i, row in pit_stats.iterrows():
                self.strategy_table.insertRow(i)
                self.strategy_table.setItem(i, 0, QtWidgets.QTableWidgetItem(f"{row['Driver']} Stops"))
                self.strategy_table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(row["Stops"])))
        self.status.setText("Team hub loaded.")

    def _handle_error(self, exc: Exception) -> None:
        self.status.setText(f"Error: {exc}")
