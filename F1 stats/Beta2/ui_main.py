"""
F1 Dashboard Beta 2 - PyQt5 GUI
Main window with controls, data display, and charts
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QComboBox, QLabel, QTableWidget,
                              QTableWidgetItem, QMessageBox, QFileDialog,
                              QProgressBar, QSplitter, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import pandas as pd

from fastf1_utils import fetch_session_data, fetch_driver_laps
from api_utils import fetch_race_results
from plot_utils import plot_lap_times

class DataFetchThread(QThread):
    """Background thread for fetching data without freezing GUI"""
    data_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, year, race, driver):
        super().__init__()
        self.year = year
        self.race = race
        self.driver = driver
    
    def run(self):
        try:
            # Fetch FastF1 data
            session = fetch_session_data(self.year, self.race)
            if session is None:
                raise RuntimeError(f"Could not load FastF1 session for {self.year} {self.race}")

            laps = fetch_driver_laps(session, self.driver)
            if laps is None:
                # Return an empty DataFrame if laps fetching failed
                import pandas as _pd
                laps = _pd.DataFrame()
            
            # Fetch Jolpica API data
            results = fetch_race_results(self.year, self.race) or []
            
            self.data_ready.emit({
                'session': session,
                'laps': laps,
                'results': results
            })
        except Exception as e:
            self.error_occurred.emit(str(e))

class MplCanvas(FigureCanvasQTAgg):
    """Matplotlib canvas for embedding charts in PyQt"""
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class F1DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_data = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("F1 Dashboard Beta 2")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # ===== CONTROLS SECTION =====
        controls_group = QGroupBox("Controls")
        controls_layout = QHBoxLayout()
        
        # Season dropdown
        self.season_label = QLabel("Season:")
        self.season_combo = QComboBox()
        self.season_combo.addItems([str(year) for year in range(2024, 2018, -1)])
        
        # Race dropdown
        self.race_label = QLabel("Race:")
        self.race_combo = QComboBox()
        self.race_combo.addItems([
            "Bahrain", "Saudi Arabia", "Australia", "Japan", "China",
            "Miami", "Emilia Romagna", "Monaco", "Canada", "Spain",
            "Austria", "Great Britain", "Hungary", "Belgium", "Netherlands",
            "Italy", "Azerbaijan", "Singapore", "United States", "Mexico",
            "Brazil", "Las Vegas", "Qatar", "Abu Dhabi"
        ])
        
        # Driver dropdown
        self.driver_label = QLabel("Driver:")
        self.driver_combo = QComboBox()
        self.driver_combo.addItems([
            "VER", "HAM", "LEC", "SAI", "PER", "RUS", "NOR", "PIA",
            "ALO", "STR", "GAS", "OCO", "TSU", "RIC", "HUL", "MAG",
            "BOT", "ZHO", "ALB", "SAR"
        ])
        
        # Fetch button
        self.fetch_btn = QPushButton("Fetch Data")
        self.fetch_btn.setStyleSheet("""
            QPushButton {
                background-color: #e10600;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c00500;
            }
        """)
        self.fetch_btn.clicked.connect(self.on_fetch_data)
        
        # Export button
        self.export_btn = QPushButton("Export to CSV")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.on_export_csv)
        
        # Add to controls layout
        controls_layout.addWidget(self.season_label)
        controls_layout.addWidget(self.season_combo)
        controls_layout.addWidget(self.race_label)
        controls_layout.addWidget(self.race_combo)
        controls_layout.addWidget(self.driver_label)
        controls_layout.addWidget(self.driver_combo)
        controls_layout.addWidget(self.fetch_btn)
        controls_layout.addWidget(self.export_btn)
        controls_layout.addStretch()
        controls_group.setLayout(controls_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # ===== DATA DISPLAY SECTION =====
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Race Results
        results_group = QGroupBox("Race Results (Jolpica API)")
        results_layout = QVBoxLayout()
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Position", "Driver", "Constructor", "Points", "Status"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        
        # Right panel - Fastest Lap & Chart
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Fastest lap info
        fastest_lap_group = QGroupBox("Fastest Lap (FastF1)")
        fastest_lap_layout = QVBoxLayout()
        self.fastest_lap_label = QLabel("No data loaded")
        self.fastest_lap_label.setFont(QFont("Arial", 12))
        fastest_lap_layout.addWidget(self.fastest_lap_label)
        fastest_lap_group.setLayout(fastest_lap_layout)
        
        # Chart
        chart_group = QGroupBox("Lap Times Chart")
        chart_layout = QVBoxLayout()
        self.canvas = MplCanvas(self, width=8, height=6)
        chart_layout.addWidget(self.canvas)
        chart_group.setLayout(chart_layout)
        
        right_layout.addWidget(fastest_lap_group)
        right_layout.addWidget(chart_group)
        
        # Add panels to splitter
        splitter.addWidget(results_group)
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 700])
        
        # ===== ADD ALL TO MAIN LAYOUT =====
        main_layout.addWidget(controls_group)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def on_fetch_data(self):
        """Slot: Handle fetch data button click"""
        year = int(self.season_combo.currentText())
        race = self.race_combo.currentText()
        driver = self.driver_combo.currentText()
        
        self.statusBar().showMessage(f"Fetching data for {driver} at {year} {race}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.fetch_btn.setEnabled(False)
        
        # Create and start background thread
        self.fetch_thread = DataFetchThread(year, race, driver)
        self.fetch_thread.data_ready.connect(self.on_data_received)
        self.fetch_thread.error_occurred.connect(self.on_data_error)
        self.fetch_thread.start()
    
    def on_data_received(self, data):
        """Slot: Handle data received from background thread"""
        self.current_data = data
        
        # Update race results table
        self.update_results_table(data['results'])
        
        # Update fastest lap info
        self.update_fastest_lap(data['laps'], data['session'])
        
        # Update chart
        self.update_chart(data['laps'], self.driver_combo.currentText())
        
        # Enable export button
        self.export_btn.setEnabled(True)
        
        # Update UI state
        self.progress_bar.setVisible(False)
        self.fetch_btn.setEnabled(True)
        self.statusBar().showMessage("Data loaded successfully!")
    
    def on_data_error(self, error_msg):
        """Slot: Handle errors from background thread"""
        self.progress_bar.setVisible(False)
        self.fetch_btn.setEnabled(True)
        self.statusBar().showMessage("Error occurred")
        
        QMessageBox.critical(self, "Error", f"Failed to fetch data:\n{error_msg}")
    
    def update_results_table(self, results):
        """Update race results table with API data"""
        if not results:
            return
        
        self.results_table.setRowCount(len(results))
        for i, result in enumerate(results):
            self.results_table.setItem(i, 0, QTableWidgetItem(str(result.get('position', 'N/A'))))
            self.results_table.setItem(i, 1, QTableWidgetItem(result.get('driver', 'N/A')))
            self.results_table.setItem(i, 2, QTableWidgetItem(result.get('constructor', 'N/A')))
            self.results_table.setItem(i, 3, QTableWidgetItem(str(result.get('points', '0'))))
            self.results_table.setItem(i, 4, QTableWidgetItem(result.get('status', 'N/A')))
    
    def update_fastest_lap(self, laps, session):
        """Update fastest lap information"""
        if laps.empty:
            self.fastest_lap_label.setText("No lap data available")
            return
        
        fastest_lap = laps.loc[laps['LapTime'].idxmin()]
        lap_time = fastest_lap['LapTime'].total_seconds()
        lap_number = fastest_lap['LapNumber']
        
        info_text = f"""
        <b>Fastest Lap:</b> {lap_time:.3f}s<br>
        <b>Lap Number:</b> {lap_number}<br>
        <b>Compound:</b> {fastest_lap.get('Compound', 'N/A')}<br>
        <b>Track Status:</b> {fastest_lap.get('TrackStatus', 'N/A')}
        """
        self.fastest_lap_label.setText(info_text)
    
    def update_chart(self, laps, driver):
        """Update lap times chart"""
        self.canvas.axes.clear()
        plot_lap_times(self.canvas.axes, laps, driver)
        self.canvas.draw()
    
    def on_export_csv(self):
        """Slot: Export session data to CSV"""
        if not self.current_data or self.current_data['laps'].empty:
            QMessageBox.warning(self, "No Data", "No data to export!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "", "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                self.current_data['laps'].to_csv(file_path, index=False)
                QMessageBox.information(self, "Success", f"Data exported to:\n{file_path}")
                self.statusBar().showMessage(f"Exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export:\n{str(e)}")