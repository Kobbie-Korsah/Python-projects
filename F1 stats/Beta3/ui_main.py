"""
F1 Dashboard Beta 3 - Main GUI with Tabbed Interface
Telemetry, Race Results, Driver Comparison
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QComboBox, QLabel, QTableWidget,
                              QTableWidgetItem, QMessageBox, QTabWidget,
                              QProgressBar, QGroupBox, QCheckBox, QListWidget,
                              QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from fastf1_utils import fetch_session_data, fetch_driver_laps, fetch_driver_telemetry
from api_utils import fetch_race_results, fetch_driver_standings
from plot_utils import (plot_speed_trace, plot_throttle_brake_gear, 
                         plot_lap_comparison, plot_telemetry_comparison)
from telemetry_utils import process_telemetry_data, compare_drivers, summarize_telemetry
from data_cache import CacheManager

class TelemetryFetchThread(QThread):
    """Background thread for fetching telemetry data"""
    data_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, year, race, drivers, lap_type='fastest'):
        super().__init__()
        self.year = year
        self.race = race
        self.drivers = drivers
        self.lap_type = lap_type
    
    def run(self):
        try:
            session = fetch_session_data(self.year, self.race)
            telemetry_data = {}
            
            for driver in self.drivers:
                telemetry = fetch_driver_telemetry(session, driver, self.lap_type)
                laps = fetch_driver_laps(session, driver)
                telemetry_data[driver] = {
                    'telemetry': telemetry,
                    'laps': laps
                }
            
            results = fetch_race_results(self.year, self.race)
            
            self.data_ready.emit({
                'session': session,
                'telemetry_data': telemetry_data,
                'results': results
            })
        except Exception as e:
            self.error_occurred.emit(str(e))

class MplCanvas(FigureCanvasQTAgg):
    """Matplotlib canvas widget"""
    def __init__(self, parent=None, width=10, height=6, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class MultiPlotCanvas(FigureCanvasQTAgg):
    """Canvas with multiple subplots"""
    def __init__(self, parent=None, nrows=2, ncols=1, width=10, height=8, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.figure = fig
        self.axes = []
        for i in range(nrows * ncols):
            ax = fig.add_subplot(nrows, ncols, i + 1)
            self.axes.append(ax)
        fig.tight_layout()
        super().__init__(fig)

class F1DashboardBeta3(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_data = None
        self.cache_manager = CacheManager()
        self.session_ready = False
        self.telem_thread = None
        self.compare_thread = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the main UI with tabs"""
        self.setWindowTitle("F1 Dashboard Beta 3 - Telemetry & Comparison")
        self.setGeometry(50, 50, 1600, 1000)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # ===== GLOBAL CONTROLS =====
        controls_group = QGroupBox("Global Controls")
        controls_layout = QHBoxLayout()
        
        self.season_label = QLabel("Season:")
        self.season_combo = QComboBox()
        self.season_combo.addItems([str(year) for year in range(2024, 2018, -1)])
        
        self.race_label = QLabel("Race:")
        self.race_combo = QComboBox()
        self.race_combo.addItems([
            "Bahrain", "Saudi Arabia", "Australia", "Japan", "China",
            "Miami", "Emilia Romagna", "Monaco", "Canada", "Spain",
            "Austria", "Great Britain", "Hungary", "Belgium", "Netherlands",
            "Italy", "Azerbaijan", "Singapore", "United States", "Mexico",
            "Brazil", "Las Vegas", "Qatar", "Abu Dhabi"
        ])
        
        self.fetch_btn = QPushButton("Fetch Session Data")
        self.fetch_btn.setStyleSheet("""
            QPushButton {
                background-color: #e10600;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c00500;
            }
        """)
        self.fetch_btn.clicked.connect(self.on_fetch_session)
        
        controls_layout.addWidget(self.season_label)
        controls_layout.addWidget(self.season_combo)
        controls_layout.addWidget(self.race_label)
        controls_layout.addWidget(self.race_combo)
        controls_layout.addWidget(self.fetch_btn)
        controls_layout.addStretch()
        controls_group.setLayout(controls_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # ===== TAB WIDGET =====
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
            }
            QTabBar::tab {
                background: #353535;
                color: white;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #e10600;
            }
        """)
        
        # Create tabs
        self.telemetry_tab = self.create_telemetry_tab()
        self.results_tab = self.create_results_tab()
        self.comparison_tab = self.create_comparison_tab()
        self.standings_tab = self.create_standings_tab()
        
        self.tabs.addTab(self.telemetry_tab, "Driver Telemetry")
        self.tabs.addTab(self.results_tab, "Race Results")
        self.tabs.addTab(self.comparison_tab, "Driver Comparison")
        self.tabs.addTab(self.standings_tab, "Standings")
        
        # Add to main layout
        main_layout.addWidget(controls_group)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.tabs)
        
        self.statusBar().showMessage("Ready - Select season and race, then fetch data")
    
    def create_telemetry_tab(self):
        """Create telemetry analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Driver selection
        driver_group = QGroupBox("Driver Selection")
        driver_layout = QHBoxLayout()
        
        self.telem_driver_combo = QComboBox()
        self.telem_driver_combo.addItems([
            "VER", "HAM", "LEC", "SAI", "PER", "RUS", "NOR", "PIA",
            "ALO", "STR", "GAS", "OCO", "TSU", "RIC", "HUL", "MAG",
            "BOT", "ZHO", "ALB", "SAR"
        ])
        
        self.lap_type_combo = QComboBox()
        self.lap_type_combo.addItems(["Fastest Lap", "Average Lap", "First Lap"])
        
        self.load_telem_btn = QPushButton("Load Telemetry")
        self.load_telem_btn.clicked.connect(self.on_load_telemetry)
        self.load_telem_btn.setEnabled(False)
        
        driver_layout.addWidget(QLabel("Driver:"))
        driver_layout.addWidget(self.telem_driver_combo)
        driver_layout.addWidget(QLabel("Lap Type:"))
        driver_layout.addWidget(self.lap_type_combo)
        driver_layout.addWidget(self.load_telem_btn)
        driver_layout.addStretch()
        driver_group.setLayout(driver_layout)
        
        # Telemetry charts
        self.telem_canvas = MultiPlotCanvas(nrows=2, ncols=1, width=12, height=10)
        
        layout.addWidget(driver_group)
        layout.addWidget(self.telem_canvas)
        
        return tab
    
    def create_results_tab(self):
        """Create race results tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        results_label = QLabel("Race Results")
        results_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Position", "Driver", "Constructor", "Points", "Status"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(results_label)
        layout.addWidget(self.results_table)
        
        return tab
    
    def create_comparison_tab(self):
        """Create driver comparison tab"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Left panel - driver selection
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        select_label = QLabel("Select Drivers to Compare (up to 3)")
        select_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.driver_list = QListWidget()
        self.driver_list.setSelectionMode(QListWidget.MultiSelection)
        drivers = ["VER", "HAM", "LEC", "SAI", "PER", "RUS", "NOR", "PIA",
                   "ALO", "STR", "GAS", "OCO", "TSU", "RIC", "HUL", "MAG",
                   "BOT", "ZHO", "ALB", "SAR"]
        self.driver_list.addItems(drivers)
        
        self.compare_btn = QPushButton("Compare Selected Drivers")
        self.compare_btn.clicked.connect(self.on_compare_drivers)
        self.compare_btn.setEnabled(False)
        
        left_layout.addWidget(select_label)
        left_layout.addWidget(self.driver_list)
        left_layout.addWidget(self.compare_btn)
        
        # Right panel - comparison charts
        self.comparison_canvas = MultiPlotCanvas(nrows=3, ncols=1, width=12, height=12)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(self.comparison_canvas)
        splitter.setSizes([300, 1200])
        
        layout.addWidget(splitter)
        
        return tab
    
    def create_standings_tab(self):
        """Create championship standings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        standings_label = QLabel("Championship Standings")
        standings_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        self.standings_table = QTableWidget()
        self.standings_table.setColumnCount(5)
        self.standings_table.setHorizontalHeaderLabels([
            "Position", "Driver", "Constructor", "Points", "Wins"
        ])
        self.standings_table.horizontalHeader().setStretchLastSection(True)
        
        self.load_standings_btn = QPushButton("Load Current Standings")
        self.load_standings_btn.clicked.connect(self.on_load_standings)
        
        layout.addWidget(standings_label)
        layout.addWidget(self.load_standings_btn)
        layout.addWidget(self.standings_table)
        
        return tab

    def set_loading(self, is_loading: bool, message: str = ""):
        """Show/hide the indeterminate progress bar and set status text."""
        self.progress_bar.setVisible(is_loading)
        self.progress_bar.setRange(0, 0 if is_loading else 1)
        self.fetch_btn.setEnabled(not is_loading)
        if message:
            self.statusBar().showMessage(message)
        elif not is_loading:
            self.statusBar().clearMessage()
    
    def on_fetch_session(self):
        """Fetch session data for selected race"""
        year = int(self.season_combo.currentText())
        race = self.race_combo.currentText()
        
        print(f"[DEBUG] Fetching session for {year} {race}")
        self.set_loading(True, f"Fetching session data for {year} {race}...")
        
        # Simple fetch for results
        try:
            print(f"[DEBUG] Calling fetch_race_results({year}, '{race}')")
            results = fetch_race_results(year, race)
            print(f"[DEBUG] Received {len(results)} results")
            if not results:
                raise ValueError("No results returned. The race may not exist yet or the network request failed.")
            
            self.update_results_table(results)
            print(f"[DEBUG] Results table updated")
            
            # Enable telemetry and comparison buttons
            self.load_telem_btn.setEnabled(True)
            self.compare_btn.setEnabled(True)
            self.session_ready = True
            
            self.set_loading(False, f"Session data loaded for {year} {race}")
            print(f"[DEBUG] Fetch completed successfully")
            
        except Exception as e:
            print(f"[ERROR] Exception occurred: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            self.session_ready = False
            self.set_loading(False, "Error occurred while fetching session data")
            QMessageBox.critical(self, "Error", f"Failed to fetch data:\n{str(e)}")
    
    def on_load_telemetry(self):
        """Load telemetry for selected driver"""
        year = int(self.season_combo.currentText())
        race = self.race_combo.currentText()
        driver = self.telem_driver_combo.currentText()
        lap_type = self.lap_type_combo.currentText().lower().replace(" ", "_")
        
        self.statusBar().showMessage(f"Loading telemetry for {driver}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.load_telem_btn.setEnabled(False)
        self.compare_btn.setEnabled(False)
        self.fetch_btn.setEnabled(False)
        
        self.telem_thread = TelemetryFetchThread(year, race, [driver], lap_type)
        self.telem_thread.data_ready.connect(self.on_telemetry_loaded)
        self.telem_thread.error_occurred.connect(self.on_data_error)
        self.telem_thread.start()
    
    def on_telemetry_loaded(self, data):
        """Handle loaded telemetry data"""
        self.progress_bar.setVisible(False)
        self.load_telem_btn.setEnabled(True)
        self.compare_btn.setEnabled(True)
        self.fetch_btn.setEnabled(True)
        
        driver = self.telem_driver_combo.currentText()
        telemetry = process_telemetry_data(data['telemetry_data'][driver]['telemetry'])
        
        if telemetry.empty:
            self.statusBar().showMessage("No telemetry available for selection")
            QMessageBox.warning(self, "No Data", "No telemetry available for the selected driver/lap.")
            return
        
        # Clear and plot
        for ax in self.telem_canvas.axes:
            ax.clear()
        
        plot_speed_trace(self.telem_canvas.axes[0], telemetry, driver)
        plot_throttle_brake_gear(self.telem_canvas.axes[1], telemetry, driver)
        
        self.telem_canvas.figure.tight_layout()
        self.telem_canvas.draw()
        
        metrics = summarize_telemetry(telemetry)
        self.statusBar().showMessage(
            f"Telemetry loaded for {driver} | "
            f"Avg {metrics['avg_speed']:.1f} km/h, Max {metrics['max_speed']:.1f} km/h"
        )
    
    def on_compare_drivers(self):
        """Compare selected drivers"""
        selected_items = self.driver_list.selectedItems()
        if len(selected_items) < 2:
            QMessageBox.warning(self, "Selection Error", "Please select at least 2 drivers")
            return
        if len(selected_items) > 3:
            QMessageBox.warning(self, "Selection Error", "Maximum 3 drivers can be compared")
            return
        
        drivers = [item.text() for item in selected_items]
        year = int(self.season_combo.currentText())
        race = self.race_combo.currentText()
        
        self.statusBar().showMessage(f"Comparing {', '.join(drivers)}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.compare_btn.setEnabled(False)
        self.load_telem_btn.setEnabled(False)
        self.fetch_btn.setEnabled(False)
        
        self.compare_thread = TelemetryFetchThread(year, race, drivers, 'fastest')
        self.compare_thread.data_ready.connect(self.on_comparison_loaded)
        self.compare_thread.error_occurred.connect(self.on_data_error)
        self.compare_thread.start()
    
    def on_comparison_loaded(self, data):
        """Handle comparison data"""
        self.progress_bar.setVisible(False)
        self.compare_btn.setEnabled(True)
        self.load_telem_btn.setEnabled(True)
        self.fetch_btn.setEnabled(True)
        
        telemetry_data = data['telemetry_data']
        if not telemetry_data:
            QMessageBox.warning(self, "No Data", "No telemetry data returned for comparison.")
            self.statusBar().showMessage("No telemetry data available for comparison")
            return

        # Clean data before plotting and summarising
        for driver, payload in telemetry_data.items():
            payload['telemetry'] = process_telemetry_data(payload.get('telemetry'))
        
        # Clear axes
        for ax in self.comparison_canvas.axes:
            ax.clear()
        
        # Plot comparisons
        plot_telemetry_comparison(
            self.comparison_canvas.axes[0],
            telemetry_data,
            'Speed',
            'Speed Comparison'
        )
        
        plot_telemetry_comparison(
            self.comparison_canvas.axes[1],
            telemetry_data,
            'Throttle',
            'Throttle Comparison'
        )
        
        # Lap time comparison
        laps_dict = {driver: data['laps'] for driver, data in telemetry_data.items()}
        plot_lap_comparison(self.comparison_canvas.axes[2], laps_dict)
        
        self.comparison_canvas.figure.tight_layout()
        self.comparison_canvas.draw()
        
        metrics = compare_drivers(telemetry_data)
        summary_bits = []
        for driver, metric in metrics.items():
            max_speed = metric.get("max_speed", 0.0)
            lap_duration = metric.get("lap_duration_s", 0.0)
            summary_bits.append(f"{driver}: max {max_speed:.0f} km/h, lap {lap_duration:.1f}s")
        
        if summary_bits:
            self.statusBar().showMessage("Comparison complete | " + " | ".join(summary_bits))
        else:
            drivers = ', '.join(telemetry_data.keys())
            self.statusBar().showMessage(f"Comparison complete: {drivers}")
    
    def on_load_standings(self):
        """Load championship standings"""
        year = int(self.season_combo.currentText())
        
        try:
            standings = fetch_driver_standings(year)
            if not standings:
                raise ValueError("No standings available for the selected season.")
            self.update_standings_table(standings)
            self.statusBar().showMessage(f"Loaded {year} championship standings")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load standings:\n{str(e)}")
    
    def update_results_table(self, results):
        """Update race results table"""
        if not results:
            return
        
        self.results_table.setRowCount(len(results))
        for i, result in enumerate(results):
            self.results_table.setItem(i, 0, QTableWidgetItem(str(result.get('position', 'N/A'))))
            self.results_table.setItem(i, 1, QTableWidgetItem(result.get('driver', 'N/A')))
            self.results_table.setItem(i, 2, QTableWidgetItem(result.get('constructor', 'N/A')))
            self.results_table.setItem(i, 3, QTableWidgetItem(str(result.get('points', '0'))))
            self.results_table.setItem(i, 4, QTableWidgetItem(result.get('status', 'N/A')))
    
    def update_standings_table(self, standings):
        """Update championship standings table"""
        if not standings:
            return
        
        self.standings_table.setRowCount(len(standings))
        for i, standing in enumerate(standings):
            self.standings_table.setItem(i, 0, QTableWidgetItem(str(standing.get('position', 'N/A'))))
            self.standings_table.setItem(i, 1, QTableWidgetItem(standing.get('driver', 'N/A')))
            self.standings_table.setItem(i, 2, QTableWidgetItem(standing.get('constructor', 'N/A')))
            self.standings_table.setItem(i, 3, QTableWidgetItem(str(standing.get('points', '0'))))
            self.standings_table.setItem(i, 4, QTableWidgetItem(str(standing.get('wins', '0'))))
    
    def on_data_error(self, error_msg):
        """Handle data fetching errors"""
        self.progress_bar.setVisible(False)
        self.fetch_btn.setEnabled(True)
        self.load_telem_btn.setEnabled(self.session_ready)
        self.compare_btn.setEnabled(self.session_ready)
        self.statusBar().showMessage("Error occurred")
        QMessageBox.critical(self, "Error", f"Failed to fetch data:\n{error_msg}")
