"""
F1 Analytics Suite - Driver Hub Module
Professional driver analysis with photos, stats, and visualizations
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout, QScrollArea,
    QProgressBar, QMessageBox, QSplitter, QFrame, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from core.threading import APIWorker
from utils.api_utils import (
    fetch_driver_profile, fetch_driver_career_stats, fetch_driver_season_results
)
from utils.plot_utils import (
    plot_season_progression, plot_qualifying_vs_race, add_hover_tooltips
)
from utils.ui_helpers import load_driver_photo, create_stat_card, get_flag_emoji


class DriverHubModule(QWidget):
    """Complete Driver Hub with profile, stats, and performance analysis"""

    def __init__(self):
        super().__init__()
        self.current_driver = None
        self.current_driver_code = None
        self.current_data = {}
        self.last_seasons = []
        self.last_results = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        selection_group = self.create_selection_panel()
        layout.addWidget(selection_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3A3A3A;
                border-radius: 5px;
                text-align: center;
                background-color: #2A2A2A;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #E10600;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.create_left_panel())
        splitter.addWidget(self.create_right_panel())
        splitter.setSizes([500, 1100])
        layout.addWidget(splitter)

    def create_selection_panel(self):
        group = QGroupBox("Driver Selection")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                color: white;
                border: 2px solid #3A3A3A;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)

        layout = QHBoxLayout()
        layout.setSpacing(15)

        layout.addWidget(QLabel("Driver:"))
        self.driver_combo = QComboBox()
        self.driver_combo.setMinimumWidth(200)
        self.driver_map = {
            "Max Verstappen": ("VER", "max_verstappen"),
            "Lewis Hamilton": ("HAM", "hamilton"),
            "Charles Leclerc": ("LEC", "leclerc"),
            "Carlos Sainz": ("SAI", "sainz"),
            "Sergio Perez": ("PER", "perez"),
            "George Russell": ("RUS", "russell"),
            "Lando Norris": ("NOR", "norris"),
            "Oscar Piastri": ("PIA", "piastri"),
            "Fernando Alonso": ("ALO", "alonso"),
            "Lance Stroll": ("STR", "stroll"),
            "Pierre Gasly": ("GAS", "gasly"),
            "Esteban Ocon": ("OCO", "ocon"),
            "Yuki Tsunoda": ("TSU", "tsunoda"),
            "Daniel Ricciardo": ("RIC", "ricciardo"),
            "Nico Hulkenberg": ("HUL", "hulkenberg"),
            "Kevin Magnussen": ("MAG", "kevin_magnussen"),
            "Valtteri Bottas": ("BOT", "bottas"),
            "Zhou Guanyu": ("ZHO", "zhou"),
            "Alexander Albon": ("ALB", "albon"),
            "Logan Sargeant": ("SAR", "sargeant")
        }
        self.driver_combo.addItems(self.driver_map.keys())
        layout.addWidget(self.driver_combo)

        layout.addWidget(QLabel("From:"))
        self.year_start = QComboBox()
        self.year_start.addItems([str(y) for y in range(2024, 2009, -1)])
        self.year_start.setCurrentText("2020")
        layout.addWidget(self.year_start)

        layout.addWidget(QLabel("To:"))
        self.year_end = QComboBox()
        self.year_end.addItems([str(y) for y in range(2024, 2009, -1)])
        self.year_end.setCurrentText("2024")
        layout.addWidget(self.year_end)

        self.load_btn = QPushButton("Load Driver Data")
        self.load_btn.clicked.connect(self.load_driver_data)
        self.load_btn.setMinimumHeight(35)
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #E10600;
                color: white;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover { background-color: #C00500; }
            QPushButton:pressed { background-color: #A00400; }
        """)
        layout.addWidget(self.load_btn)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def create_left_panel(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        self.profile_card = self.create_profile_card()
        layout.addWidget(self.profile_card)

        self.stats_group = self.create_stats_group()
        layout.addWidget(self.stats_group)

        self.constructor_group = self.create_constructor_group()
        layout.addWidget(self.constructor_group)

        layout.addStretch()
        scroll.setWidget(widget)
        return scroll

    def create_profile_card(self):
        card = QGroupBox("Driver Profile")
        card.setStyleSheet("""
            QGroupBox {
                background-color: #252525;
                border: 2px solid #3A3A3A;
                border-radius: 10px;
                padding: 20px;
                font-size: 11pt;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        photo_container = QWidget()
        photo_layout = QHBoxLayout(photo_container)
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(180, 180)
        self.photo_label.setStyleSheet("""
            QLabel {
                background-color: #1E1E1E;
                border: 3px solid #E10600;
                border-radius: 10px;
            }
        """)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setText("No Photo")
        self.photo_label.setScaledContents(True)
        photo_layout.addWidget(self.photo_label)
        photo_layout.addStretch()
        layout.addWidget(photo_container)

        self.name_label = QLabel("Name: -")
        self.name_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #E10600;")
        layout.addWidget(self.name_label)

        info_grid = QGridLayout()
        info_grid.setSpacing(10)
        labels = [
            ("Nationality:", "nationality_label"),
            ("Number:", "number_label"),
            ("Born:", "dob_label"),
            ("Debut:", "debut_label")
        ]
        for i, (label_text, attr_name) in enumerate(labels):
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold; color: #AAAAAA;")
            value = QLabel("-")
            value.setStyleSheet("color: white; font-size: 10pt;")
            info_grid.addWidget(label, i, 0)
            info_grid.addWidget(value, i, 1)
            setattr(self, attr_name, value)
        layout.addLayout(info_grid)
        card.setLayout(layout)
        return card

    def create_stats_group(self):
        group = QGroupBox("Career Statistics")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #252525;
                border: 2px solid #3A3A3A;
                border-radius: 10px;
                padding: 20px;
                font-size: 11pt;
                font-weight: bold;
            }
        """)

        layout = QGridLayout()
        layout.setSpacing(15)
        stats_info = [
            ("Championships", "championships"),
            ("Wins", "wins"),
            ("Podiums", "podiums"),
            ("Poles", "poles"),
            ("Fastest Laps", "fastest_laps"),
            ("Points", "points"),
            ("DNFs", "dnfs"),
            ("Races", "races")
        ]
        self.stats_labels = {}
        for i, (title, key) in enumerate(stats_info):
            stat_widget = create_stat_card(title, "-")
            layout.addWidget(stat_widget, i // 2, (i % 2))
            value_label = stat_widget.findChild(QLabel, "statValue")
            # Fallback in case objectName mismatch
            if value_label is None:
                labels = stat_widget.findChildren(QLabel)
                value_label = labels[-1] if labels else None
                if value_label is not None:
                    value_label.setObjectName("statValue")
            self.stats_labels[key] = value_label
        group.setLayout(layout)
        return group

    def create_constructor_group(self):
        group = QGroupBox("Constructor History")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #252525;
                border: 2px solid #3A3A3A;
                border-radius: 10px;
                padding: 20px;
                font-size: 11pt;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout()
        self.constructor_table = QTableWidget()
        self.constructor_table.setColumnCount(3)
        self.constructor_table.setHorizontalHeaderLabels(["Season", "Team", "Position"])
        self.constructor_table.horizontalHeader().setStretchLastSection(True)
        self.constructor_table.setMaximumHeight(250)
        layout.addWidget(self.constructor_table)
        group.setLayout(layout)
        return group

    def create_right_panel(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        self.season_canvas = FigureCanvasQTAgg(Figure(figsize=(14, 5), facecolor='#1E1E1E'))
        season_group = QGroupBox("Season Points Progression")
        season_layout = QVBoxLayout()
        season_layout.addWidget(self.season_canvas)
        season_group.setLayout(season_layout)
        layout.addWidget(season_group)
        self.season_canvas.mousePressEvent = lambda event: self.show_chart_popup("season")

        self.quali_canvas = FigureCanvasQTAgg(Figure(figsize=(14, 5), facecolor='#1E1E1E'))
        quali_group = QGroupBox("Qualifying vs Race Performance")
        quali_layout = QVBoxLayout()
        quali_layout.addWidget(self.quali_canvas)
        quali_group.setLayout(quali_layout)
        layout.addWidget(quali_group)
        self.quali_canvas.mousePressEvent = lambda event: self.show_chart_popup("quali")

        results_group = QGroupBox("Season Results")
        results_layout = QVBoxLayout()
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "Race", "Round", "Grid", "Position", "Points", "Status", "Fastest Lap"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        self.results_table.horizontalHeader().sectionClicked.connect(self.show_table_popup)

        scroll.setWidget(widget)
        return scroll

    def load_driver_data(self):
        driver_name = self.driver_combo.currentText()
        driver_code, driver_id = self.driver_map[driver_name]
        year_start = int(self.year_start.currentText())
        year_end = int(self.year_end.currentText())
        if year_start > year_end:
            QMessageBox.warning(self, "Invalid Range", "Start year must be before or equal to end year")
            return
        self.current_driver_code = driver_code
        self.current_driver = driver_id

        self.load_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        pixmap = load_driver_photo(driver_code, (180, 180))
        self.photo_label.setPixmap(pixmap)

        self.api_worker = APIWorker(self.fetch_all_driver_data, driver_id, driver_code, year_start, year_end)
        self.api_worker.data_ready.connect(self.on_data_loaded)
        self.api_worker.error_occurred.connect(self.on_error)
        self.api_worker.start()

    def fetch_all_driver_data(self, driver_id, driver_code, year_start, year_end):
        data = {}
        data['profile'] = fetch_driver_profile(driver_id)
        data['career'] = fetch_driver_career_stats(driver_id)
        data['seasons'] = []
        for year in range(year_start, year_end + 1):
            season_data = fetch_driver_season_results(driver_id, year)
            if season_data:
                data['seasons'].append({'year': year, 'results': season_data})
        return data

    def on_data_loaded(self, result):
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)

        data = result['result']
        self.current_data = data
        self.last_seasons = data.get('seasons', [])

        self.update_profile(data.get('profile', {}), data.get('career', {}))
        self.update_career_stats(data.get('career', {}))
        self.update_season_charts(self.last_seasons)
        self.update_results_table(self.last_seasons)

        QMessageBox.information(self, "Success",
                                f"Driver data loaded successfully for {self.driver_combo.currentText()}")

    def update_profile(self, profile, career_stats=None):
        name = profile.get('name', '-') or '-'
        nationality = profile.get('nationality', '-') or '-'
        flag = get_flag_emoji(nationality)
        self.name_label.setText(name)
        self.nationality_label.setText(f"{flag} {nationality}".strip())
        number = profile.get('number') or '-'
        self.number_label.setText(f"#{number}")
        self.dob_label.setText(profile.get('dob', '-') or '-')
        debut = (
            profile.get('debut')
            or profile.get('debut_year')
            or (career_stats or {}).get('debut')
            or '-'
        )
        self.debut_label.setText(str(debut))

    def update_career_stats(self, stats):
        for key, label in self.stats_labels.items():
            if label:
                label.setText("-")
        if self.stats_labels.get('championships'):
            self.stats_labels['championships'].setText(str(stats.get('championships', 0)))
        if self.stats_labels.get('wins'):
            self.stats_labels['wins'].setText(str(stats.get('wins', 0)))
        if self.stats_labels.get('podiums'):
            self.stats_labels['podiums'].setText(str(stats.get('podiums', 0)))
        if self.stats_labels.get('poles'):
            self.stats_labels['poles'].setText(str(stats.get('poles', 0)))
        if self.stats_labels.get('fastest_laps'):
            self.stats_labels['fastest_laps'].setText(str(stats.get('fastest_laps', 0)))
        if self.stats_labels.get('points'):
            self.stats_labels['points'].setText(f"{stats.get('points', 0):.0f}")
        if self.stats_labels.get('dnfs'):
            self.stats_labels['dnfs'].setText(str(stats.get('dnfs', 0)))
        if self.stats_labels.get('races'):
            self.stats_labels['races'].setText(str(stats.get('races', 0)))

    def update_season_charts(self, seasons):
        if not seasons:
            return
        self.season_canvas.figure.clear()
        ax1 = self.season_canvas.figure.add_subplot(111)
        plot_season_progression(ax1, seasons, self.current_driver_code)
        add_hover_tooltips(ax1)
        self.season_canvas.draw()

        self.quali_canvas.figure.clear()
        ax2 = self.quali_canvas.figure.add_subplot(111)
        plot_qualifying_vs_race(ax2, seasons, self.current_driver_code)
        add_hover_tooltips(ax2)
        self.quali_canvas.draw()

    def update_results_table(self, seasons):
        if not seasons:
            self.results_table.setRowCount(0)
            return
        latest = seasons[-1]['results']
        self.last_results = latest
        self.results_table.setRowCount(len(latest))
        for i, result in enumerate(latest):
            self.results_table.setItem(i, 0, QTableWidgetItem(result.get('race', '-')))
            self.results_table.setItem(i, 1, QTableWidgetItem(str(result.get('round', '-'))))
            self.results_table.setItem(i, 2, QTableWidgetItem(str(result.get('grid', '-'))))
            self.results_table.setItem(i, 3, QTableWidgetItem(str(result.get('position', '-'))))
            self.results_table.setItem(i, 4, QTableWidgetItem(str(result.get('points', '-'))))
            self.results_table.setItem(i, 5, QTableWidgetItem(result.get('status', '-')))
            self.results_table.setItem(i, 6, QTableWidgetItem(str(result.get('fastest_lap', '-'))))

    def show_chart_popup(self, chart_type: str):
        if not self.last_seasons:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Full Chart")
        dlg_layout = QVBoxLayout(dialog)
        canvas = FigureCanvasQTAgg(Figure(figsize=(16, 7), facecolor='#1E1E1E'))
        dlg_layout.addWidget(canvas)
        ax = canvas.figure.add_subplot(111)
        if chart_type == "season":
            plot_season_progression(ax, self.last_seasons, self.current_driver_code)
        else:
            plot_qualifying_vs_race(ax, self.last_seasons, self.current_driver_code)
        canvas.draw()
        dialog.resize(1000, 700)
        dialog.exec()

    def show_table_popup(self, *_):
        if not self.last_results:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Full Season Results")
        layout = QVBoxLayout(dlg)
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Race", "Round", "Grid", "Position", "Points", "Status", "Fastest Lap"
        ])
        table.setRowCount(len(self.last_results))
        for i, result in enumerate(self.last_results):
            table.setItem(i, 0, QTableWidgetItem(result.get('race', '-')))
            table.setItem(i, 1, QTableWidgetItem(str(result.get('round', '-'))))
            table.setItem(i, 2, QTableWidgetItem(str(result.get('grid', '-'))))
            table.setItem(i, 3, QTableWidgetItem(str(result.get('position', '-'))))
            table.setItem(i, 4, QTableWidgetItem(str(result.get('points', '-'))))
            table.setItem(i, 5, QTableWidgetItem(result.get('status', '-')))
            table.setItem(i, 6, QTableWidgetItem(str(result.get('fastest_lap', '-'))))
        table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(table)
        dlg.resize(900, 600)
        dlg.exec()

    def on_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Failed to load data:\n{error_msg}")

    def export_data(self):
        if not self.current_data:
            QMessageBox.warning(self, "No Data", "Load driver data first")
            return
        # Placeholder for export implementation
        pass
