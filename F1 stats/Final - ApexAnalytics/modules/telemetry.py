"""
F1 Analytics Suite - Telemetry Module
Complete telemetry visualization with speed, throttle, brake, gear traces
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QComboBox, QGroupBox, QProgressBar,
                              QMessageBox, QDialog)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from core.threading import TelemetryWorker
from utils.plot_utils import plot_speed_trace, plot_throttle_brake_gear
from pathlib import Path
import traceback

class TelemetryModule(QWidget):
    """Telemetry visualization module"""
    
    def __init__(self):
        super().__init__()
        self.current_data = None
        self.last_driver = None
        self.last_telemetry = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize telemetry interface"""
        layout = QVBoxLayout(self)
        
        # Controls
        controls = self.create_controls()
        layout.addWidget(controls)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Charts
        self.speed_canvas = FigureCanvasQTAgg(Figure(figsize=(16, 6), facecolor='#1E1E1E'))
        speed_group = QGroupBox("Speed Trace")
        speed_layout = QVBoxLayout()
        speed_layout.addWidget(self.speed_canvas)
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        self.speed_canvas.mousePressEvent = lambda event: self.show_chart_popup("speed")
        
        self.input_canvas = FigureCanvasQTAgg(Figure(figsize=(16, 6), facecolor='#1E1E1E'))
        input_group = QGroupBox("Throttle, Brake & Gear")
        input_layout = QVBoxLayout()
        input_layout.addWidget(self.input_canvas)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        self.input_canvas.mousePressEvent = lambda event: self.show_chart_popup("inputs")
    
    def create_controls(self) -> QWidget:
        """Create control widgets"""
        controls_widget = QWidget()
        layout = QHBoxLayout()
        
        layout.addWidget(QLabel("Session:"))
        self.session_combo = QComboBox()
        self.session_combo.addItems(["Race", "Qualifying"])
        layout.addWidget(self.session_combo)
        
        layout.addWidget(QLabel("Driver:"))
        self.driver_combo = QComboBox()
        self.driver_combo.addItems([
            "VER", "PER", "HAM", "RUS", "LEC", "SAI", "NOR", "PIA",
            "ALO", "STR", "GAS", "OCO", "RIC", "TSU", "BOT", "ZHO",
            "HUL", "MAG", "ALB", "SAR"
        ])
        layout.addWidget(self.driver_combo)
        
        self.load_button = QPushButton("Load Telemetry")
        self.load_button.clicked.connect(self.on_load_telemetry)
        layout.addWidget(self.load_button)
        
        layout.addStretch()
        controls_widget.setLayout(layout)
        return controls_widget

    def _log_error(self, message: str):
        """Append errors to logs/error.log for diagnostics."""
        log_dir = Path(__file__).resolve().parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "error.log"
        with log_file.open("a", encoding="utf-8") as f:
            f.write(message + "\n")
    
    def on_load_telemetry(self):
        """Load and display telemetry data"""
        if not self.driver_combo.currentText():
            QMessageBox.warning(self, "Error", "Please select a driver")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Create worker thread
        session_type = "R" if self.session_combo.currentText() == "Race" else "Q"
        try:
            worker = TelemetryWorker(2024, "Bahrain", [self.driver_combo.currentText()], session_type)
            worker.data_ready.connect(self.on_data_ready)
            worker.error_occurred.connect(self.on_error)
            worker.progress_update.connect(self.on_progress)
            self.worker = worker  # keep reference
            worker.start()
        except Exception as exc:
            self.progress_bar.setVisible(False)
            self._log_error(f"Failed to start telemetry worker: {exc}")
            QMessageBox.critical(self, "Error", f"Failed to start telemetry fetch: {exc}")
    
    def on_data_ready(self, data):
        """Handle telemetry data"""
        try:
            self.current_data = data
            self.progress_bar.setVisible(False)
            self.update_charts()
        except Exception as exc:
            self.progress_bar.setVisible(False)
            tb = traceback.format_exc()
            self._log_error(f"Telemetry on_data_ready failed: {exc}\n{tb}")
            QMessageBox.critical(self, "Error", f"Failed to render telemetry:\n{exc}")
    
    def on_error(self, error):
        """Handle error"""
        self.progress_bar.setVisible(False)
        self._log_error(f"Telemetry worker error: {error}")
        QMessageBox.critical(self, "Error", f"Failed to load telemetry: {error}")
    
    def on_progress(self, value, message):
        """Update progress"""
        self.progress_bar.setValue(value)
    
    def update_charts(self):
        """Update telemetry charts"""
        if not self.current_data:
            return
        try:
            # Use the first driver's data (only one driver is fetched at a time here)
            driver, payload = next(iter(self.current_data.items()))
            telemetry = payload.get('telemetry')
            if telemetry is None or getattr(telemetry, "empty", False):
                raise ValueError("No telemetry data returned")
            self.last_driver = driver
            self.last_telemetry = telemetry
            
            # Clear old plots
            self.speed_canvas.figure.clear()
            self.input_canvas.figure.clear()
            
            ax_speed = self.speed_canvas.figure.add_subplot(111)
            plot_speed_trace(ax_speed, telemetry, driver)
            self.speed_canvas.draw()
            
            ax_inputs = self.input_canvas.figure.add_subplot(111)
            plot_throttle_brake_gear(ax_inputs, telemetry, driver)
            self.input_canvas.draw()
        except Exception as exc:
            tb = traceback.format_exc()
            self._log_error(f"Telemetry update_charts failed: {exc}\n{tb}")
            QMessageBox.critical(self, "Error", f"Failed to render telemetry:\n{exc}")

    def show_chart_popup(self, kind: str):
        """Open enlarged telemetry chart."""
        if self.last_telemetry is None or self.last_driver is None:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Telemetry")
        layout = QVBoxLayout(dlg)
        canvas = FigureCanvasQTAgg(Figure(figsize=(18, 8), facecolor='#1E1E1E'))
        layout.addWidget(canvas)
        ax = canvas.figure.add_subplot(111)
        if kind == "speed":
            plot_speed_trace(ax, self.last_telemetry, self.last_driver)
        else:
            plot_throttle_brake_gear(ax, self.last_telemetry, self.last_driver)
        canvas.draw()
        dlg.resize(1100, 800)
        dlg.exec()
