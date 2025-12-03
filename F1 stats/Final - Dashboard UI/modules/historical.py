"""
Historical Lens module for multi-season trajectories.
"""

import pandas as pd
from PyQt6 import QtWidgets

from core.threading import run_in_thread
from utils import api_utils


class HistoricalLensModule(QtWidgets.QWidget):
    """Generates driver/team trajectories across a year range."""

    def __init__(self) -> None:
        super().__init__()
        self._worker = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.entity_id = QtWidgets.QLineEdit()
        self.entity_id.setPlaceholderText("Driver or Constructor ID")
        self.is_driver = QtWidgets.QCheckBox("Is Driver (unchecked = Team)")
        self.start_year = QtWidgets.QSpinBox()
        self.start_year.setRange(1950, 2050)
        self.start_year.setValue(2019)
        self.end_year = QtWidgets.QSpinBox()
        self.end_year.setRange(1950, 2050)
        self.end_year.setValue(2023)
        form.addRow("Entity ID", self.entity_id)
        form.addRow("", self.is_driver)
        form.addRow("Start", self.start_year)
        form.addRow("End", self.end_year)
        layout.addLayout(form)

        btn = QtWidgets.QPushButton("Generate History")
        btn.clicked.connect(self._start_generate)
        layout.addWidget(btn)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Season", "Metric", "Value"])
        layout.addWidget(self.table)

        self.status = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status)

    def _start_generate(self) -> None:
        entity = self.entity_id.text().strip()
        if not entity:
            self.status.setText("Enter an ID.")
            return
        self.status.setText("Building history...")
        self._worker = run_in_thread(
            self._build_history,
            on_result=self._handle_result,
            on_error=self._handle_error,
            entity=entity,
            is_driver=self.is_driver.isChecked(),
            start_year=self.start_year.value(),
            end_year=self.end_year.value(),
            api_key=None,
        )

    @staticmethod
    def _build_history(entity: str, is_driver: bool, start_year: int, end_year: int, api_key=None) -> pd.DataFrame:
        rows = []
        for season in range(start_year, end_year + 1):
            if is_driver:
                stats = api_utils.fetch_driver_stats(entity, api_key) or {}
                rows.append((season, "Points", stats.get("points", 0)))
                rows.append((season, "Wins", stats.get("wins", 0)))
            else:
                standings = api_utils.fetch_constructor_standings(entity, api_key) or {}
                rows.append((season, "Points", standings.get("points", 0)))
                rows.append((season, "Wins", standings.get("wins", 0)))
        return pd.DataFrame(rows, columns=["Season", "Metric", "Value"])

    def _handle_result(self, df: pd.DataFrame) -> None:
        self.table.setRowCount(len(df))
        for i, row in df.iterrows():
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(row["Season"])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(row["Metric"])))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(row["Value"])))
        self.status.setText("History generated.")

    def _handle_error(self, exc: Exception) -> None:
        self.status.setText(f"Error: {exc}")
