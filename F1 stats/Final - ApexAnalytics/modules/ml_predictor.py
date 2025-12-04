"""
F1 Analytics Suite - ML Predictor Module
Machine Learning predictions for race outcomes
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QGroupBox, QProgressBar, QMessageBox, QTextEdit, QSpinBox
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np

from utils.plot_utils import plot_feature_importance


class MLPredictorModule(QWidget):
    """Machine Learning predictions module"""

    def __init__(self):
        super().__init__()
        self.model = None
        self.feature_names = []
        self.init_ui()

    def init_ui(self):
        """Initialize ML predictor interface"""
        layout = QVBoxLayout(self)

        controls = self.create_controls()
        layout.addWidget(controls)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results display
        h_layout = QHBoxLayout()

        # Predictions panel
        predictions_group = QGroupBox("Predictions")
        predictions_layout = QVBoxLayout()

        self.predictions_text = QTextEdit()
        self.predictions_text.setReadOnly(True)
        self.predictions_text.setMaximumHeight(320)
        self.predictions_text.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #3A3A3A;
                border-radius: 6px;
                padding: 10px;
                font-family: monospace;
                font-size: 11pt;
            }
        """)

        predictions_layout.addWidget(self.predictions_text)
        predictions_group.setLayout(predictions_layout)
        h_layout.addWidget(predictions_group)

        # Feature importance
        importance_group = QGroupBox("Feature Importance")
        importance_layout = QVBoxLayout()

        self.importance_canvas = FigureCanvasQTAgg(Figure(figsize=(8, 6), facecolor='#1E1E1E'))
        importance_layout.addWidget(self.importance_canvas)

        importance_group.setLayout(importance_layout)
        h_layout.addWidget(importance_group)

        layout.addLayout(h_layout)

    def create_controls(self):
        """Create ML controls"""
        group = QGroupBox("ML Predictor Setup")
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Training Years:"))
        self.years_combo = QComboBox()
        self.years_combo.addItems(["2019-2023", "2020-2024", "2018-2022"])
        layout.addWidget(self.years_combo)

        self.train_btn = QPushButton("Train Model")
        self.train_btn.clicked.connect(self.train_model)
        self.train_btn.setStyleSheet("""
            QPushButton {
                background-color: #0090FF;
                color: white;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {background-color: #0070DD;}
        """)
        layout.addWidget(self.train_btn)

        layout.addWidget(QLabel("Driver:"))
        self.driver_combo = QComboBox()
        self.driver_combo.addItems(["VER", "HAM", "LEC", "SAI", "PER", "RUS"])
        layout.addWidget(self.driver_combo)

        # Prediction inputs
        layout.addWidget(QLabel("Quali Pos"))
        self.quali_spin = QSpinBox()
        self.quali_spin.setRange(1, 20)
        self.quali_spin.setValue(5)
        layout.addWidget(self.quali_spin)

        layout.addWidget(QLabel("Team Points"))
        self.team_points_spin = QSpinBox()
        self.team_points_spin.setRange(0, 1000)
        self.team_points_spin.setValue(80)
        layout.addWidget(self.team_points_spin)

        layout.addWidget(QLabel("Track Type"))
        self.track_combo = QComboBox()
        self.track_combo.addItems(["Permanent", "Street", "Hybrid"])
        layout.addWidget(self.track_combo)

        layout.addWidget(QLabel("Pit Stops"))
        self.pit_spin = QSpinBox()
        self.pit_spin.setRange(0, 5)
        self.pit_spin.setValue(2)
        layout.addWidget(self.pit_spin)

        layout.addWidget(QLabel("Weather (0-10)"))
        self.weather_spin = QSpinBox()
        self.weather_spin.setRange(0, 10)
        self.weather_spin.setValue(7)
        layout.addWidget(self.weather_spin)

        self.predict_btn = QPushButton("Predict")
        self.predict_btn.clicked.connect(self.predict_performance)
        self.predict_btn.setEnabled(False)
        self.predict_btn.setStyleSheet("""
            QPushButton {
                background-color: #E10600;
                color: white;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {background-color: #C00500;}
        """)
        layout.addWidget(self.predict_btn)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def train_model(self):
        """Train ML model"""
        try:
            # Lazy import to avoid crashing if sklearn is missing
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
        except Exception as exc:
            self.progress_bar.setVisible(False)
            self.train_btn.setEnabled(True)
            QMessageBox.critical(
                self,
                "Missing Dependency",
                "scikit-learn is required for the ML Predictor.\n"
                "Install with: pip install scikit-learn\n\n"
                f"Details: {exc}"
            )
            return

        self.train_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        # Generate synthetic training data (placeholder; swap with real features if available)
        np.random.seed(42)
        n_samples = 500

        # Features: qualifying_pos, team_points, track_type, pit_stops, weather
        X = np.random.rand(n_samples, 5)
        X[:, 0] = 1 + X[:, 0] * 19  # Qualifying position (1-20)
        X[:, 1] = X[:, 1] * 500     # Team points
        X[:, 2] = X[:, 2] * 2       # Track type (0-2)
        X[:, 3] = X[:, 3] * 4       # Pit stops (0-4)
        X[:, 4] = X[:, 4] * 10      # Weather score (0-10)

        # Target: Race finish position (lower is better) with some noise
        y = X[:, 0] * 0.65 + X[:, 3] * 0.4 + np.random.randn(n_samples) * 1.5

        self.feature_names = ['Qualifying Pos', 'Team Points', 'Track Type', 'Pit Stops', 'Weather']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train Random Forest
        self.model = RandomForestRegressor(n_estimators=120, random_state=42, max_depth=8)
        self.model.fit(X_train, y_train)

        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        # Display results
        self.predictions_text.setPlainText(
            f"=== MODEL TRAINING COMPLETE ===\n\n"
            f"Model: Random Forest Regressor\n"
            f"Training Samples: {len(X_train)}\n"
            f"Test Samples: {len(X_test)}\n\n"
            f"Training R^2 Score: {train_score:.3f}\n"
            f"Test R^2 Score: {test_score:.3f}\n\n"
            f"Model is ready for predictions.\n"
        )

        # Plot feature importance
        self.importance_canvas.figure.clear()
        ax = self.importance_canvas.figure.add_subplot(111)
        plot_feature_importance(ax, self.feature_names, self.model.feature_importances_)
        self.importance_canvas.draw()

        self.progress_bar.setVisible(False)
        self.train_btn.setEnabled(True)
        self.predict_btn.setEnabled(True)

        QMessageBox.information(self, "Success", "Model trained successfully!")

    def predict_performance(self):
        """Make predictions"""
        if self.model is None:
            QMessageBox.warning(self, "No Model", "Please train the model first")
            return

        driver = self.driver_combo.currentText()

        # Build feature vector from UI inputs
        quali = float(self.quali_spin.value())
        team_pts = float(self.team_points_spin.value())
        track_map = {"Permanent": 0.0, "Street": 1.0, "Hybrid": 2.0}
        track = track_map.get(self.track_combo.currentText(), 0.0)
        pits = float(self.pit_spin.value())
        weather = float(self.weather_spin.value())

        sample_input = np.array([[quali, team_pts, track, pits, weather]])

        prediction = self.model.predict(sample_input)[0]

        # Calculate confidence interval (simplified)
        std_dev = 2.0  # Estimated std deviation
        confidence_lower = prediction - 1.96 * std_dev
        confidence_upper = prediction + 1.96 * std_dev

        self.predictions_text.setPlainText(
            f"=== RACE PREDICTION FOR {driver} ===\n\n"
            f"Input Features:\n"
            f"  - Qualifying Position: {quali}\n"
            f"  - Team Points: {team_pts}\n"
            f"  - Track Type: {self.track_combo.currentText()}\n"
            f"  - Expected Pit Stops: {pits}\n"
            f"  - Weather Score: {weather}/10\n\n"
            f"PREDICTED RACE FINISH:\n"
            f"  Position: {prediction:.1f}\n\n"
            f"95% Confidence Interval:\n"
            f"  Lower: {confidence_lower:.1f}\n"
            f"  Upper: {confidence_upper:.1f}\n\n"
            f"Notes:\n"
            f"  - Qualifying and pit strategy influence outcome most in this toy model.\n"
            f"  - Weather/track type provide secondary adjustment.\n"
        )

        QMessageBox.information(
            self,
            "Prediction Complete",
            f"Predicted finish: P{int(round(prediction))}"
        )

    def export_data(self):
        """Export ML model"""
        pass
