"""
F1 Analytics Suite - Analytics Module
Season and team performance analytics
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QGroupBox, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from core.threading import GenericWorker
from utils.api_utils import fetch_driver_standings, fetch_constructor_standings
from utils.plot_utils import add_hover_tooltips


class AnalyticsModule(QWidget):
    """Analytics visualization module with driver/constructor snapshots"""

    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        """Initialize analytics interface"""
        layout = QVBoxLayout(self)

        controls = self.create_controls()
        layout.addWidget(controls)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.canvas = FigureCanvasQTAgg(Figure(figsize=(14, 7), facecolor='#1E1E1E'))
        layout.addWidget(self.canvas)

    def create_controls(self) -> QWidget:
        """Create control widgets"""
        controls_widget = QWidget()
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Season:"))
        self.year_combo = QComboBox()
        self.year_combo.addItems([str(y) for y in range(2024, 2013, -1)])
        layout.addWidget(self.year_combo)

        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.clicked.connect(self.on_analyze)
        layout.addWidget(self.analyze_button)

        layout.addStretch()
        controls_widget.setLayout(layout)
        return controls_widget

    def on_analyze(self):
        """Kick off analytics fetch and plotting"""
        if self.worker and self.worker.isRunning():
            return

        year = int(self.year_combo.currentText())
        self.analyze_button.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)

        self.worker = GenericWorker(self._load_analytics_data, year)
        self.worker.finished.connect(self._on_data_ready)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _load_analytics_data(self, year: int):
        """Fetch standings for driver/constructor analytics"""
        drivers = fetch_driver_standings(year)
        constructors = fetch_constructor_standings(year)
        return {'drivers': drivers, 'constructors': constructors, 'year': year}

    def _on_data_ready(self, data):
        self.progress.setVisible(False)
        self.analyze_button.setEnabled(True)

        if not data or (not data.get('drivers') and not data.get('constructors')):
            QMessageBox.information(self, "No Data", "No standings data available for this season.")
            return

        self._plot_snapshots(data)
        QMessageBox.information(self, "Analytics Ready",
                                f"Season {data.get('year')} analytics rendered.")

    def _plot_snapshots(self, data: dict):
        """Render driver and constructor bar charts"""
        fig = self.canvas.figure
        fig.clear()

        drivers = sorted(data.get('drivers', []), key=lambda d: d.get('points', 0), reverse=True)[:10]
        constructors = sorted(data.get('constructors', []), key=lambda c: float(c.get('points', 0)), reverse=True)[:10]

        # Ensure two subplots even if one list is empty
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)

        if drivers:
            names = [f"{d.get('name', '')} ({d.get('code', '')})" for d in drivers]
            points = [d.get('points', 0) for d in drivers]
            ax1.barh(names, points, color="#E10600")
            ax1.invert_yaxis()
            ax1.set_title("Top Drivers - Points", color="white", fontsize=12, fontweight="bold")
            ax1.set_xlabel("Points", color="white")
            ax1.tick_params(colors="white")
            ax1.set_facecolor("#1E1E1E")
            for spine in ax1.spines.values():
                spine.set_color("#3A3A3A")
            add_hover_tooltips(ax1, xfmt=lambda v: f"{v:.1f} pts", yfmt=lambda v: f"{v:.0f}")
        else:
            ax1.text(0.5, 0.5, "No driver data", ha="center", va="center", color="white")
            ax1.set_facecolor("#1E1E1E")

        if constructors:
            names_c = [c.get('constructor') for c in constructors]
            points_c = [float(c.get('points', 0)) for c in constructors]
            ax2.barh(names_c, points_c, color="#005AFF")
            ax2.invert_yaxis()
            ax2.set_title("Constructors - Points", color="white", fontsize=12, fontweight="bold")
            ax2.set_xlabel("Points", color="white")
            ax2.tick_params(colors="white")
            ax2.set_facecolor("#1E1E1E")
            for spine in ax2.spines.values():
                spine.set_color("#3A3A3A")
            add_hover_tooltips(ax2, xfmt=lambda v: f"{v:.1f} pts", yfmt=lambda v: f"{v:.0f}")
        else:
            ax2.text(0.5, 0.5, "No constructor data", ha="center", va="center", color="white")
            ax2.set_facecolor("#1E1E1E")

        fig.tight_layout()
        self.canvas.draw()

    def _on_error(self, msg: str):
        self.progress.setVisible(False)
        self.analyze_button.setEnabled(True)
        QMessageBox.critical(self, "Analytics Error", msg)
