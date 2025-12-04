"""
F1 Analytics Suite - Main UI Window
Multi-tab interface with Driver/Team mode switching
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QTabWidget, QPushButton, QLabel, QComboBox,
                              QStatusBar, QMenuBar, QMenu, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon

from modules.driver_hub import DriverHubModule
from modules.team_hub import TeamHubModule
from modules.telemetry import TelemetryModule
from modules.comparison import ComparisonModule
from modules.analytics import AnalyticsModule
from modules.ml_predictor import MLPredictorModule
from core.enums import AppMode

class F1AnalyticsSuite(QMainWindow):
    """Main application window with tabbed interface"""
    
    mode_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_mode = AppMode.DRIVER
        self.init_ui()
        self.setup_menu_bar()
        
    def init_ui(self):
        """Initialize the main user interface"""
        self.setWindowTitle("ApexAnalytics - Professional Edition")
        self.setGeometry(50, 50, 1800, 1000)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(False)
        self.tabs.setDocumentMode(True)
        
        # Create all tabs
        self.home_tab = self.create_home_tab()
        self.driver_hub = DriverHubModule()
        self.team_hub = TeamHubModule()
        self.telemetry_tab = TelemetryModule()
        self.comparison_tab = ComparisonModule()
        self.analytics_tab = AnalyticsModule()
        self.ml_predictor_tab = MLPredictorModule()

        # Add tabs
        self.tabs.addTab(self.home_tab, "Home")
        self.driver_hub_index = self.tabs.addTab(self.driver_hub, "Driver Hub")
        self.team_hub_index = self.tabs.addTab(self.team_hub, "Team Hub")
        self.tabs.addTab(self.telemetry_tab, "Telemetry")
        self.tabs.addTab(self.comparison_tab, "Comparison")
        self.tabs.addTab(self.analytics_tab, "Analytics")
        self.tabs.addTab(self.ml_predictor_tab, "ML Predictor")

        # Initially show Driver Hub
        self.update_hub_visibility()
        
        main_layout.addWidget(self.tabs)
        
        # Status Bar
        self.statusBar().showMessage("Ready - Select a season and race to begin")
        
    def create_header(self):
        """Create application header with mode switcher"""
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(80)
        layout = QHBoxLayout(header)
        
        # Title
        title = QLabel("ApexAnalytics")
        title.setObjectName("appTitle")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #E10600;
            padding: 10px;
        """)
        
        # Season selector
        season_label = QLabel("Season:")
        self.season_combo = QComboBox()
        self.season_combo.addItems([str(year) for year in range(2024, 2017, -1)])
        self.season_combo.setMinimumWidth(100)
        
        # Race selector
        race_label = QLabel("Race:")
        self.race_combo = QComboBox()
        self.race_combo.addItems([
            "Bahrain", "Saudi Arabia", "Australia", "Japan", "China",
            "Miami", "Emilia Romagna", "Monaco", "Canada", "Spain",
            "Austria", "Great Britain", "Hungary", "Belgium", "Netherlands",
            "Italy", "Azerbaijan", "Singapore", "United States", "Mexico",
            "Brazil", "Las Vegas", "Qatar", "Abu Dhabi"
        ])
        self.race_combo.setMinimumWidth(150)
        
        # Mode switcher
        mode_label = QLabel("Mode:")
        self.mode_switch = QPushButton("Switch to Team Mode")
        self.mode_switch.setCheckable(True)
        self.mode_switch.clicked.connect(self.toggle_mode)
        self.mode_switch.setStyleSheet("""
            QPushButton {
                background-color: #E10600;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C00500;
            }
        """)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(season_label)
        layout.addWidget(self.season_combo)
        layout.addWidget(race_label)
        layout.addWidget(self.race_combo)
        layout.addSpacing(20)
        layout.addWidget(mode_label)
        layout.addWidget(self.mode_switch)
        
        return header
    
    def create_home_tab(self):
        """Create home/welcome tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        welcome = QLabel("""
            <h1 style='color: #E10600;'>Welcome to ApexAnalytics</h1>
            <h3>Your Complete Formula 1 Data Analysis Platform</h3>
            <br>
            <p style='font-size: 14px;'>
            <b>Features:</b><br>
            - <b>Driver Hub:</b> Comprehensive driver profiles with photos<br>
            - <b>Team Hub:</b> Constructor insights with team logos<br>
            - <b>Telemetry:</b> Detailed lap-by-lap visualization<br>
            - <b>Comparison:</b> Head-to-head performance analysis<br>
            - <b>Analytics:</b> Advanced race pace and strategy analysis<br>
            - <b>ML Predictor:</b> Machine learning race predictions<br>
            <br>
            <b>Getting Started:</b><br>
            1. Select a season and race from the header<br>
            2. Choose Driver or Team mode<br>
            3. Navigate through tabs to explore analyses<br>
            4. Export your findings as PNG, CSV, or JSON<br>
            </p>
        """)
        welcome.setWordWrap(True)
        welcome.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        layout.addWidget(welcome)

        terms_button = QPushButton("Terms and Conditions")
        terms_button.setFixedWidth(200)
        terms_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #E10600; }
            """
        )
        terms_button.clicked.connect(self.show_terms)
        layout.addWidget(terms_button)
        layout.addStretch()

        return tab
    
    def setup_menu_bar(self):
        """Setup application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        export_action = QAction("&Export Current View", self)
        export_action.triggered.connect(self.export_current_view)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        clear_cache_action = QAction("Clear Cache", self)
        clear_cache_action.triggered.connect(self.clear_cache)
        tools_menu.addAction(clear_cache_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def toggle_mode(self):
        """Toggle between Driver and Team mode"""
        if self.current_mode == AppMode.DRIVER:
            self.current_mode = AppMode.TEAM
            self.mode_switch.setText("Switch to Driver Mode")
        else:
            self.current_mode = AppMode.DRIVER
            self.mode_switch.setText("Switch to Team Mode")
        
        self.update_hub_visibility()
        self.mode_changed.emit(self.current_mode.value)
        self.statusBar().showMessage(f"Switched to {self.current_mode.value} mode")
    
    def update_hub_visibility(self):
        """Update tab visibility based on current mode"""
        if self.current_mode == AppMode.DRIVER:
            self.tabs.setTabVisible(self.driver_hub_index, True)
            self.tabs.setTabVisible(self.team_hub_index, False)
        else:
            self.tabs.setTabVisible(self.driver_hub_index, False)
            self.tabs.setTabVisible(self.team_hub_index, True)
    
    def export_current_view(self):
        """Export current tab view"""
        current_index = self.tabs.currentIndex()
        current_widget = self.tabs.widget(current_index)
        
        if hasattr(current_widget, 'export_data'):
            current_widget.export_data()
        else:
            QMessageBox.information(
                self,
                "Export",
                "Export functionality not available for this tab"
            )
    
    def clear_cache(self):
        """Clear application cache"""
        from core.data_cache import CacheManager
        cache = CacheManager()
        cache.clear_all()
        QMessageBox.information(self, "Cache Cleared", "Application cache has been cleared")
        self.statusBar().showMessage("Cache cleared successfully")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About F1 Analytics Suite",
            """
            <h2>F1 Analytics Suite v1.0.0</h2>
            <p>Professional Formula 1 Data Analysis Platform</p>
            <br>
            <p><b>Built with:</b></p>
            <ul>
                <li>PyQt6 - Modern UI Framework</li>
                <li>FastF1 - Official F1 Telemetry Data</li>
                <li>Jolpica F1 API - Historical Race Data</li>
                <li>Scikit-learn - Machine Learning</li>
                <li>Matplotlib - Data Visualization</li>
            </ul>
            <br>
            <p>© 2024 F1 Analytics Suite</p>
            """
        )
    
    def get_selected_season(self):
        """Get currently selected season"""
        return int(self.season_combo.currentText())
    
    def get_selected_race(self):
        """Get currently selected race"""
        return self.race_combo.currentText()

    def show_terms(self):
        """Display Terms & Conditions dialog"""
        QMessageBox.information(
            self,
            "Terms & Conditions",
            (
                "This application is provided for personal, non-commercial use.\n\n"
                "Data is sourced from FastF1 and the Jolpica/Ergast API; availability "
                "and accuracy are not guaranteed.\n\n"
                "Use at your own risk. The authors are not responsible for any losses, "
                "damages, or data issues arising from use of this software.\n\n"
                "By continuing, you agree to respect third-party data terms and ensure "
                "you have rights to any images or assets you add."
            ),
        )
