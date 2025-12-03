"""
Main window UI composition for the F1 Analytics dashboard.
Provides tab management, mode switching, and wiring to module widgets.
"""

from PyQt6 import QtCore, QtGui, QtWidgets

from core.enums import HubMode
from modules.analytics import AnalyticsModule
from modules.comparison import ComparisonModule
from modules.constructors import ConstructorsModule
from modules.driver_hub import DriverHubModule
from modules.ml_predictor import MLPredictorModule
from modules.telemetry import TelemetryModule
from modules.team_hub import TeamHubModule
from modules.historical import HistoricalLensModule
from utils.ui_helpers import build_toolbar_toggle, set_tab_visibility


class MainWindow(QtWidgets.QMainWindow):
    """Top-level window containing all navigation and modules."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("F1 Analytics Dashboard")
        self.resize(1400, 900)
        self._hub_mode = HubMode.DRIVER
        self._build_ui()
        self._apply_styles()
        self._connect_signals()

    def _build_ui(self) -> None:
        """Compose the central widget and tabs."""
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        root_layout = QtWidgets.QVBoxLayout(central)
        self.toolbar = QtWidgets.QToolBar("Mode")
        self.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        self.mode_toggle = build_toolbar_toggle(self.toolbar, "Driver Mode", "Team Mode")

        self.tabs = QtWidgets.QTabWidget()
        root_layout.addWidget(self.tabs)

        self.home_tab = self._build_home_tab()
        self.driver_tab = DriverHubModule()
        self.team_tab = TeamHubModule()
        self.telemetry_tab = TelemetryModule()
        self.comparison_tab = ComparisonModule()
        self.analytics_tab = AnalyticsModule()
        self.historical_tab = HistoricalLensModule()
        self.ml_tab = MLPredictorModule()
        self.constructors_tab = ConstructorsModule()

        self.tabs.addTab(self.home_tab, "Home")
        self.tabs.addTab(self.driver_tab, "Driver Hub")
        self.tabs.addTab(self.team_tab, "Team Hub")
        self.tabs.addTab(self.telemetry_tab, "Telemetry")
        self.tabs.addTab(self.comparison_tab, "Comparison")
        self.tabs.addTab(self.analytics_tab, "Analytics")
        self.tabs.addTab(self.historical_tab, "Historical Lens")
        self.tabs.addTab(self.ml_tab, "ML Predictor")
        self.tabs.addTab(self.constructors_tab, "Export/Constructors")

        self._update_mode_tabs()

    def _build_home_tab(self) -> QtWidgets.QWidget:
        """Build the landing page with instructions."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        title = QtWidgets.QLabel("F1 Analytics Suite")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("heroTitle")

        subtitle = QtWidgets.QLabel(
            "Multi-threaded FastF1 + Jolpica analytics. Use the toggle to switch between Driver and Team hubs."
        )
        subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        return widget

    def _apply_styles(self) -> None:
        """Load styles if the stylesheet exists."""
        try:
            with open("styles.qss", "r", encoding="utf-8") as fh:
                self.setStyleSheet(fh.read())
        except FileNotFoundError:
            pass

    def _connect_signals(self) -> None:
        """Wire up UI events."""
        self.mode_toggle.stateChanged.connect(self._handle_mode_switch)

    def _handle_mode_switch(self, state: int) -> None:
        """Toggle between driver and team hub visibility."""
        self._hub_mode = HubMode.TEAM if state == QtCore.Qt.CheckState.Checked.value else HubMode.DRIVER
        self._update_mode_tabs()

    def _update_mode_tabs(self) -> None:
        """Hide/show tabs based on current mode."""
        driver_visible = self._hub_mode == HubMode.DRIVER
        team_visible = self._hub_mode == HubMode.TEAM
        set_tab_visibility(self.tabs, self.driver_tab, driver_visible)
        set_tab_visibility(self.tabs, self.team_tab, team_visible)

