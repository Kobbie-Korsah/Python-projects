"""
F1 Analytics Suite - Constructors Module
Constructor/Team performance and standings
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QComboBox, QTableWidget,
                              QTableWidgetItem, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from core.threading import GenericWorker

class ConstructorsModule(QWidget):
    """Constructor/Team analytics module"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize constructors interface"""
        layout = QVBoxLayout(self)
        
        # Controls
        controls = self.create_controls()
        layout.addWidget(controls)
        
        # Standings table
        self.standings_table = QTableWidget()
        self.standings_table.setColumnCount(5)
        self.standings_table.setHorizontalHeaderLabels(["Position", "Team", "Points", "Wins", "Podiums"])
        layout.addWidget(self.standings_table)
        
        # Chart area
        self.canvas = FigureCanvasQTAgg(Figure(figsize=(14, 5), facecolor='#1E1E1E'))
        layout.addWidget(self.canvas)
    
    def create_controls(self) -> QWidget:
        """Create control widgets"""
        controls_widget = QWidget()
        layout = QHBoxLayout()
        
        layout.addWidget(QLabel("Season:"))
        self.season_combo = QComboBox()
        self.season_combo.addItems(["2024", "2023", "2022"])
        layout.addWidget(self.season_combo)
        
        self.load_button = QPushButton("Load Standings")
        self.load_button.clicked.connect(self.on_load_standings)
        layout.addWidget(self.load_button)
        
        layout.addStretch()
        controls_widget.setLayout(layout)
        return controls_widget
    
    def on_load_standings(self):
        """Load constructor standings"""
        QMessageBox.information(self, "Constructors", "Constructors module - under development")
