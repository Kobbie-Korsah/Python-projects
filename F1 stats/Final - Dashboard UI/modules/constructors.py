"""
Constructors/Export module handling team data and global export shortcuts.
"""

import pandas as pd
from PyQt6 import QtWidgets

from core.enums import ExportFormat
from core.threading import run_in_thread
from utils import api_utils


class ConstructorsModule(QtWidgets.QWidget):
    """Displays constructor standings and supports exports."""

    def __init__(self) -> None:
        super().__init__()
        self._worker = None
        self._last_df: pd.DataFrame | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.constructor_id = QtWidgets.QLineEdit()
        self.constructor_id.setPlaceholderText("Constructor ID (e.g., red_bull)")
        self.api_key = QtWidgets.QLineEdit()
        self.api_key.setPlaceholderText("Jolpica API key (optional)")
        form.addRow("Constructor ID", self.constructor_id)
        form.addRow("API Key", self.api_key)
        layout.addLayout(form)

        btns = QtWidgets.QHBoxLayout()
        fetch_btn = QtWidgets.QPushButton("Load Constructor")
        fetch_btn.clicked.connect(self._start_fetch)
        export_csv = QtWidgets.QPushButton("Export CSV")
        export_csv.clicked.connect(lambda: self._export(ExportFormat.CSV))
        export_json = QtWidgets.QPushButton("Export JSON")
        export_json.clicked.connect(lambda: self._export(ExportFormat.JSON))
        for b in (fetch_btn, export_csv, export_json):
            btns.addWidget(b)
        layout.addLayout(btns)

        self.table = QtWidgets.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Field", "Value"])
        layout.addWidget(self.table)
        self.status = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status)

    def _start_fetch(self) -> None:
        constructor_id = self.constructor_id.text().strip()
        if not constructor_id:
            self.status.setText("Enter a constructor ID.")
            return
        self.status.setText("Loading constructor data...")
        self._worker = run_in_thread(
            self._load_constructor,
            on_result=self._handle_result,
            on_error=self._handle_error,
            constructor_id=constructor_id,
            api_key=self.api_key.text().strip() or None,
        )

    @staticmethod
    def _load_constructor(constructor_id: str, api_key: str | None):
        profile = api_utils.fetch_constructor(constructor_id, api_key)
        standings = api_utils.fetch_constructor_standings(constructor_id, api_key)
        return {"profile": profile, "standings": standings}

    def _handle_result(self, data) -> None:
        flattened = []
        for section, values in data.items():
            if isinstance(values, dict):
                for k, v in values.items():
                    flattened.append((f"{section}.{k}", v))
        self._last_df = pd.DataFrame(flattened, columns=["Field", "Value"])
        self.table.setRowCount(len(flattened))
        for i, (k, v) in enumerate(flattened):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(k)))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(v)))
        self.status.setText("Constructor data loaded.")

    def _handle_error(self, exc: Exception) -> None:
        self.status.setText(f"Error: {exc}")

    def _export(self, fmt: ExportFormat) -> None:
        if self._last_df is None:
            self.status.setText("Nothing to export.")
            return
        if fmt == ExportFormat.CSV:
            self._last_df.to_csv("constructor_export.csv", index=False)
            self.status.setText("Saved constructor_export.csv")
        elif fmt == ExportFormat.JSON:
            self._last_df.to_json("constructor_export.json", orient="records")
            self.status.setText("Saved constructor_export.json")
