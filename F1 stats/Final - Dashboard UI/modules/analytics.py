"""
Analytics module for pace consistency and strategy simulation.
Contains export hooks for markdown/PNG summaries.
"""

import io
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
from PyQt6 import QtWidgets

from core.enums import ExportFormat
from core.threading import run_in_thread
from utils import fastf1_utils, plot_utils
from utils.ui_helpers import add_export_buttons


class AnalyticsModule(QtWidgets.QWidget):
    """High-level analytics across qualifying and race performance."""

    def __init__(self) -> None:
        super().__init__()
        self._worker = None
        self._last_df: Optional[pd.DataFrame] = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)

        control = QtWidgets.QHBoxLayout()
        self.season = QtWidgets.QSpinBox()
        self.season.setRange(1950, 2050)
        self.season.setValue(2023)
        self.round_no = QtWidgets.QSpinBox()
        self.round_no.setRange(1, 25)
        self.round_no.setValue(1)
        load_btn = QtWidgets.QPushButton("Compute Race Pace Consistency")
        load_btn.clicked.connect(self._start_compute)
        for w in (QtWidgets.QLabel("Season"), self.season, QtWidgets.QLabel("Round"), self.round_no, load_btn):
            control.addWidget(w)
        layout.addLayout(control)

        self.figure = plt.Figure(figsize=(7, 4))
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.status = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status)

        add_export_buttons(
            self,
            {
                "Export PNG": lambda: self._export(ExportFormat.PNG),
                "Export CSV": lambda: self._export(ExportFormat.CSV),
                "Export MD": lambda: self._export(ExportFormat.MARKDOWN),
            },
        )

    def _start_compute(self) -> None:
        season = self.season.value()
        round_no = self.round_no.value()
        self.status.setText("Calculating pace consistency...")
        self._worker = run_in_thread(
            self._compute_pace_consistency,
            on_result=self._handle_result,
            on_error=self._handle_error,
            season=season,
            round_no=round_no,
        )

    @staticmethod
    def _compute_pace_consistency(season: int, round_no: int) -> pd.DataFrame:
        session = fastf1_utils.load_session(season, round_no, "R")
        if not session:
            raise RuntimeError("Failed to load race session")
        laps = fastf1_utils.get_laps(session)
        summary = laps.groupby("Driver")["LapTime"].agg(["mean", "std"]).reset_index()
        summary = summary.rename(columns={"mean": "AvgLap", "std": "StdDev"})
        summary = summary.sort_values("StdDev")
        return summary

    def _handle_result(self, df: pd.DataFrame) -> None:
        self._last_df = df
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.bar(df["Driver"], df["StdDev"], color="#e10600")
        plot_utils.style_axes(ax, "Race Pace Consistency (lower = better)")
        ax.set_ylabel("Std Dev Lap Time (s)")
        self.canvas.draw()
        self.status.setText("Analytics computed.")

    def _handle_error(self, exc: Exception) -> None:
        self.status.setText(f"Error: {exc}")

    def _export(self, fmt: ExportFormat) -> None:
        if self._last_df is None:
            self.status.setText("Nothing to export yet.")
            return
        if fmt == ExportFormat.CSV:
            self._last_df.to_csv("analytics_summary.csv", index=False)
            self.status.setText("Saved analytics_summary.csv")
        elif fmt == ExportFormat.MARKDOWN:
            buf = io.StringIO()
            buf.write("# Race Pace Consistency\n\n")
            buf.write(self._last_df.to_markdown(index=False))
            with open("analytics_summary.md", "w", encoding="utf-8") as fh:
                fh.write(buf.getvalue())
            self.status.setText("Saved analytics_summary.md")
        elif fmt == ExportFormat.PNG:
            self.figure.savefig("analytics_summary.png", dpi=150, bbox_inches="tight")
            self.status.setText("Saved analytics_summary.png")
