"""
F1 Analytics Suite - Team Hub Module
Professional team analysis with logos, stats, and driver comparison
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
                              QGroupBox, QGridLayout, QScrollArea, QProgressBar,
                              QMessageBox, QSplitter, QFrame, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from core.threading import APIWorker
from utils.api_utils import (fetch_constructor_profile, fetch_constructor_standings,
                               fetch_race_results, fetch_constructor_results)
from utils.plot_utils import plot_lap_comparison, plot_telemetry_comparison, add_hover_tooltips
from utils.ui_helpers import load_team_logo, load_driver_photo, create_stat_card

class TeamHubModule(QWidget):
    """Complete Team Hub with profile, performance, and strategy analysis"""
    
    def __init__(self):
        super().__init__()
        self.current_team = None
        self.last_standings = []
        self.current_data = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize team hub interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Team selection
        selection = self.create_selection_panel()
        layout.addWidget(selection)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Main content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left = self.create_left_panel()
        right = self.create_right_panel()
        
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([500, 1100])
        
        layout.addWidget(splitter)
    
    def create_selection_panel(self):
        """Create team selection panel"""
        group = QGroupBox("Team Selection")
        layout = QHBoxLayout()
        
        self.team_combo = QComboBox()
        self.team_map = {
            "Red Bull Racing": "red_bull",
            "Mercedes": "mercedes",
            "Ferrari": "ferrari",
            "McLaren": "mclaren",
            "Aston Martin": "aston_martin",
            "Alpine": "alpine",
            "Williams": "williams",
            "AlphaTauri": "alphatauri",
            "Alfa Romeo": "alfa",
            "Haas F1 Team": "haas"
        }
        self.team_combo.addItems(self.team_map.keys())
        
        self.year_combo = QComboBox()
        self.year_combo.addItems([str(y) for y in range(2024, 2009, -1)])
        
        self.load_btn = QPushButton("Load Team Data")
        self.load_btn.clicked.connect(self.load_team_data)
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #E10600;
                color: white;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C00500;
            }
        """)
        
        layout.addWidget(QLabel("Team:"))
        layout.addWidget(self.team_combo)
        layout.addWidget(QLabel("Season:"))
        layout.addWidget(self.year_combo)
        layout.addWidget(self.load_btn)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def create_left_panel(self):
        """Create left panel with team profile"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Team profile card
        self.profile_card = QGroupBox("Team Profile")
        profile_layout = QVBoxLayout()
        
        # Logo
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(200, 120)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setStyleSheet("background-color: #1E1E1E; border-radius: 10px;")
        profile_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Team info
        self.team_name_label = QLabel("Team: -")
        self.team_name_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #E10600;")
        profile_layout.addWidget(self.team_name_label)
        
        self.nationality_label = QLabel("Nationality: -")
        profile_layout.addWidget(self.nationality_label)
        
        self.profile_card.setLayout(profile_layout)
        layout.addWidget(self.profile_card)
        
        # Team stats
        self.stats_group = QGroupBox("Team Statistics")
        stats_layout = QGridLayout()
        
        self.stats_labels = {}
        stats_info = [
            ("Championships", "championships"),
            ("Wins", "wins"),
            ("Podiums", "podiums"),
            ("Points", "points")
        ]
        
        for i, (title, key) in enumerate(stats_info):
            stat_card = create_stat_card(title, "-")
            stats_layout.addWidget(stat_card, i // 2, i % 2)
            # Store reference to value label (fallback to last QLabel if name mismatch)
            value_label = stat_card.findChild(QLabel, "statValue")
            if value_label is None:
                labels = stat_card.findChildren(QLabel)
                value_label = labels[-1] if labels else None
                if value_label is not None:
                    value_label.setObjectName("statValue")
            self.stats_labels[key] = value_label
        
        self.stats_group.setLayout(stats_layout)
        layout.addWidget(self.stats_group)
        
        layout.addStretch()
        scroll.setWidget(widget)
        return scroll
    
    def create_right_panel(self):
        """Create right panel with charts"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Standings table
        self.standings_group = QGroupBox("Constructor Standings")
        standings_layout = QVBoxLayout()
        
        self.standings_table = QTableWidget()
        self.standings_table.setColumnCount(4)
        self.standings_table.setHorizontalHeaderLabels(["Position", "Constructor", "Points", "Wins"])
        self.standings_table.horizontalHeader().setStretchLastSection(True)
        
        standings_layout.addWidget(self.standings_table)
        self.standings_group.setLayout(standings_layout)
        layout.addWidget(self.standings_group)
        self.standings_table.horizontalHeader().sectionClicked.connect(self.show_standings_popup)
        
        # Season performance chart
        perf_group = QGroupBox("Season Performance (Cumulative Points)")
        perf_layout = QVBoxLayout()
        self.perf_canvas = FigureCanvasQTAgg(Figure(figsize=(10, 4), facecolor='#1E1E1E'))
        perf_layout.addWidget(self.perf_canvas)
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        return widget
    
    def load_team_data(self):
        """Load team data"""
        team_name = self.team_combo.currentText()
        team_id = self.team_map[team_name]
        year = int(self.year_combo.currentText())
        
        self.current_team = team_id
        
        # Load team logo
        pixmap = load_team_logo(team_name, (200, 120))
        self.logo_label.setPixmap(pixmap)
        
        self.load_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        # Fetch data
        self.api_worker = APIWorker(
            self.fetch_team_data,
            team_id,
            year
        )
        self.api_worker.data_ready.connect(self.on_data_loaded)
        self.api_worker.error_occurred.connect(self.on_error)
        self.api_worker.start()
    
    def fetch_team_data(self, team_id, year):
        """Fetch all team data"""
        data = {}
        data['profile'] = fetch_constructor_profile(team_id)
        data['standings'] = fetch_constructor_standings(year)
        data['results'] = fetch_constructor_results(year, team_id)
        return data
    
    def on_data_loaded(self, result):
        """Handle loaded data"""
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        
        data = result['result']
        self.current_data = data
        
        # Update UI
        profile = data.get('profile', {})
        self.team_name_label.setText(profile.get('name', '-'))
        self.nationality_label.setText(f"Nationality: {profile.get('nationality', '-')}")
        
        # Update standings
        standings = data.get('standings', [])
        self.last_standings = standings
        self.standings_table.setRowCount(len(standings))
        
        for i, standing in enumerate(standings):
            self.standings_table.setItem(i, 0, QTableWidgetItem(str(standing.get('position', '-'))))
            self.standings_table.setItem(i, 1, QTableWidgetItem(standing.get('constructor', '-')))
            self.standings_table.setItem(i, 2, QTableWidgetItem(str(standing.get('points', '-'))))
            self.standings_table.setItem(i, 3, QTableWidgetItem(str(standing.get('wins', '-'))))

        # Populate stats for the selected team (season snapshot)
        team_entry = next((s for s in standings if s.get('constructor_id') == self.current_team), None)
        if team_entry:
            champs = "1" if str(team_entry.get('position')) == "1" else "0"
            self.stats_labels.get('championships') and self.stats_labels['championships'].setText(champs)
            self.stats_labels.get('wins') and self.stats_labels['wins'].setText(str(team_entry.get('wins', 0)))
            results = data.get('results', [])
            podiums = sum(r.get('podiums', 0) for r in results)
            self.stats_labels.get('podiums') and self.stats_labels['podiums'].setText(str(podiums))
            self.stats_labels.get('points') and self.stats_labels['points'].setText(str(team_entry.get('points', 0)))
        else:
            for label in self.stats_labels.values():
                label.setText("-")

        # Season performance chart
        self.update_performance_chart(data.get('results', []))
        
        QMessageBox.information(self, "Success", "Team data loaded successfully")
    
    def on_error(self, error_msg):
        """Handle errors"""
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Failed to load data:\n{error_msg}")

    def update_performance_chart(self, results):
        """Plot cumulative points across the season."""
        ax = self.perf_canvas.figure.subplots()
        ax.clear()

        if not results:
            ax.text(0.5, 0.5, "No performance data", ha="center", va="center",
                    transform=ax.transAxes, fontsize=12, color="white")
            self.perf_canvas.draw()
            return

        ordered = sorted([r for r in results if r.get('round')], key=lambda r: r['round'])
        rounds = [r['round'] for r in ordered]
        cumulative = []
        total = 0.0
        for r in ordered:
            total += float(r.get('points', 0))
            cumulative.append(total)

        ax.plot(rounds, cumulative, color="#E10600", linewidth=2, marker="o")
        ax.set_facecolor("#1E1E1E")
        ax.grid(True, linestyle="--", alpha=0.2, color="#3A3A3A")
        ax.set_xlabel("Round", color="white", fontsize=11, fontweight="bold")
        ax.set_ylabel("Cumulative Points", color="white", fontsize=11, fontweight="bold")
        ax.set_title("Season Performance", color="#E10600", fontsize=13, fontweight="bold")
        ax.tick_params(colors="white")
        add_hover_tooltips(ax, xfmt=lambda v: f"Round {v:.0f}", yfmt=lambda v: f"{v:.1f} pts")
        self.perf_canvas.figure.tight_layout()
        self.perf_canvas.draw()

    def show_standings_popup(self, *_):
        """Open enlarged standings table"""
        if not self.last_standings:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Full Constructor Standings")
        layout = QVBoxLayout(dlg)
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Position", "Constructor", "Points", "Wins"])
        table.setRowCount(len(self.last_standings))
        for i, standing in enumerate(self.last_standings):
            table.setItem(i, 0, QTableWidgetItem(str(standing.get('position', '-'))))
            table.setItem(i, 1, QTableWidgetItem(standing.get('constructor', '-')))
            table.setItem(i, 2, QTableWidgetItem(str(standing.get('points', '-'))))
            table.setItem(i, 3, QTableWidgetItem(str(standing.get('wins', '-'))))
        table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(table)
        dlg.resize(800, 600)
        dlg.exec()
    
    def export_data(self):
        """Export team data"""
        pass
