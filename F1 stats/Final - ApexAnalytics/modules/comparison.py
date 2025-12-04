"""
F1 Analytics Suite - Comparison Module
Compare drivers performance
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QGroupBox, QListWidget, QListWidgetItem, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from core.threading import GenericWorker
from utils.api_utils import fetch_driver_standings, fetch_driver_season_results
from utils.plot_utils import add_hover_tooltips


class ComparisonModule(QWidget):
    """Driver comparison module"""

    def __init__(self):
        super().__init__()
        self.standings_cache = []
        self.worker = None
        self.init_ui()
        self.load_driver_list()

    def init_ui(self):
        """Initialize comparison interface"""
        layout = QVBoxLayout(self)

        controls = self.create_controls()
        layout.addWidget(controls)

        selection_group = QGroupBox("Select Drivers for Comparison")
        selection_layout = QHBoxLayout()

        self.driver_list = QListWidget()
        # MultiSelection lets users click multiple rows without holding Ctrl.
        self.driver_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.driver_list.setMinimumHeight(260)

        list_container = QVBoxLayout()
        list_container.addWidget(QLabel("Drivers (click multiple):"))
        list_container.addWidget(self.driver_list)
        selection_layout.addLayout(list_container)

        helper_col = QVBoxLayout()
        helper_col.addWidget(QLabel("Quick actions"))

        self.top2_btn = QPushButton("Select Top 2")
        self.top2_btn.clicked.connect(lambda: self.quick_select(2))
        helper_col.addWidget(self.top2_btn)

        self.top4_btn = QPushButton("Select Top 4")
        self.top4_btn.clicked.connect(lambda: self.quick_select(4))
        helper_col.addWidget(self.top4_btn)

        self.clear_btn = QPushButton("Clear Selection")
        self.clear_btn.clicked.connect(self.driver_list.clearSelection)
        helper_col.addWidget(self.clear_btn)

        helper_col.addStretch()
        selection_layout.addLayout(helper_col)

        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

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
        self.year_combo.currentTextChanged.connect(self.load_driver_list)
        layout.addWidget(self.year_combo)

        layout.addWidget(QLabel("Metric:"))
        self.metric_combo = QComboBox()
        self.metric_combo.addItems(["Points", "Wins", "Podiums", "Avg Finish Position"])
        layout.addWidget(self.metric_combo)

        self.compare_button = QPushButton("Compare")
        self.compare_button.clicked.connect(self.on_compare)
        layout.addWidget(self.compare_button)

        layout.addStretch()
        controls_widget.setLayout(layout)
        return controls_widget

    def load_driver_list(self, *_):
        """Populate list with season driver standings"""
        year = int(self.year_combo.currentText())
        standings = fetch_driver_standings(year)
        self.standings_cache = standings
        self.driver_list.clear()
        for driver in standings:
            text = f"{driver.get('name', '')} ({driver.get('code', '')})"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, driver)
            self.driver_list.addItem(item)
        # Preselect top 2 for a quick default comparison
        self.quick_select(2)

    def quick_select(self, count: int):
        """Helper to select top N drivers."""
        self.driver_list.blockSignals(True)
        self.driver_list.clearSelection()
        for i in range(min(count, self.driver_list.count())):
            self.driver_list.item(i).setSelected(True)
        self.driver_list.blockSignals(False)

    def on_compare(self):
        """Perform comparison using background worker"""
        if self.worker and self.worker.isRunning():
            return

        selected_items = self.driver_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Select Drivers", "Pick at least one driver to compare.")
            return

        metric = self.metric_combo.currentText()
        year = int(self.year_combo.currentText())
        drivers = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]

        self.compare_button.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)

        self.worker = GenericWorker(self._build_comparison_data, drivers, year, metric)
        self.worker.finished.connect(self._on_results_ready)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _build_comparison_data(self, drivers, year, metric):
        """Compute metric values for selected drivers"""
        results = []
        for drv in drivers:
            driver_id = drv.get('driver_id')
            name = drv.get('name', driver_id)
            code = drv.get('code', '')
            season_results = fetch_driver_season_results(driver_id, year) or []

            wins = sum(1 for r in season_results if str(r.get('position', "")) == "1")
            podiums = sum(1 for r in season_results if r.get('position') and int(r.get('position')) <= 3)
            finish_positions = [int(r.get('position')) for r in season_results if str(r.get('position', "")).isdigit()]
            avg_finish = (sum(finish_positions) / len(finish_positions)) if finish_positions else None
            points = next((d.get('points') for d in self.standings_cache if d.get('driver_id') == driver_id), 0)

            if metric == "Points":
                value = points
            elif metric == "Wins":
                value = wins
            elif metric == "Podiums":
                value = podiums
            else:
                # Avg Finish Position - lower is better
                value = avg_finish if avg_finish is not None else 99

            results.append({
                'name': name,
                'code': code,
                'value': value,
                'invert': metric == "Avg Finish Position"
            })

        return {'metric': metric, 'year': year, 'results': results}

    def _on_results_ready(self, data):
        self.progress.setVisible(False)
        self.compare_button.setEnabled(True)

        if not data or not data.get('results'):
            QMessageBox.information(self, "No Data", "No comparison data available.")
            return

        self._plot_results(data)
        QMessageBox.information(self, "Comparison Ready",
                                f"{data.get('metric')} comparison for {data.get('year')} updated.")

    def _plot_results(self, data: dict):
        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)

        metric = data.get('metric')
        results = data.get('results', [])

        # Sort appropriately (desc except avg finish)
        reverse = False if metric == "Avg Finish Position" else True
        results = sorted(results, key=lambda r: r['value'] if r['value'] is not None else 0, reverse=reverse)

        names = [f"{r['name']} ({r['code']})" for r in results]
        values = [r['value'] for r in results]
        colors = "#E10600" if metric != "Avg Finish Position" else "#00D2BE"

        ax.barh(names, values, color=colors)
        if metric == "Avg Finish Position":
            ax.invert_xaxis()
        ax.invert_yaxis()
        ax.set_title(f"{metric} - Season {data.get('year')}", color="white", fontsize=12, fontweight="bold")
        ax.tick_params(colors="white")
        ax.set_xlabel(metric, color="white")
        ax.set_facecolor("#1E1E1E")
        for spine in ax.spines.values():
            spine.set_color("#3A3A3A")
        xfmt = (lambda v: f"P{v:.1f}") if metric == "Avg Finish Position" else (lambda v: f"{v:.1f}")
        add_hover_tooltips(ax, xfmt=xfmt, yfmt=lambda v: "")

        fig.tight_layout()
        self.canvas.draw()

    def _on_error(self, msg: str):
        self.progress.setVisible(False)
        self.compare_button.setEnabled(True)
        QMessageBox.critical(self, "Comparison Error", msg)
