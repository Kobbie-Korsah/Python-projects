"""
ML Predictor module training a simple RandomForestRegressor on synthetic F1 stats.
"""

import numpy as np
import pandas as pd
from PyQt6 import QtWidgets
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score


class MLPredictorModule(QtWidgets.QWidget):
    """Trains and displays predictions for qualifying and race finish positions."""

    def __init__(self) -> None:
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        self.train_btn = QtWidgets.QPushButton("Train Model")
        self.train_btn.clicked.connect(self._train_model)
        layout.addWidget(self.train_btn)

        self.output = QtWidgets.QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

    def _train_model(self) -> None:
        """Train a quick model on synthetic 5-season data."""
        df = self._generate_dataset()
        features = ["QualPos", "TeamPoints", "DriverPoints", "TrackType", "PitStops", "DNFs"]
        target = "FinishPos"
        X = df[features]
        y = df[target]
        categorical = ["TrackType"]
        numeric = [f for f in features if f not in categorical]

        pre = ColumnTransformer(
            [("cat", OneHotEncoder(handle_unknown="ignore"), categorical), ("num", "passthrough", numeric)]
        )
        model = RandomForestRegressor(n_estimators=120, random_state=42)
        pipe = Pipeline([("pre", pre), ("model", model)])
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        score = r2_score(y_test, preds)
        sample = df.iloc[0:1][features]
        pred_sample = pipe.predict(sample)[0]

        self.output.setPlainText(
            f"Model trained on {len(df)} samples\n"
            f"R2 Score: {score:.3f}\n"
            f"Sample prediction (finish pos): {pred_sample:.2f}\n"
            f"Feature columns: {features}"
        )

    @staticmethod
    def _generate_dataset(rows: int = 500) -> pd.DataFrame:
        """Create synthetic but structured dataset for demo purposes."""
        rng = np.random.default_rng(42)
        data = {
            "QualPos": rng.integers(1, 20, rows),
            "FinishPos": rng.integers(1, 20, rows),
            "TeamPoints": rng.integers(0, 600, rows),
            "DriverPoints": rng.integers(0, 300, rows),
            "TrackType": rng.choice(["street", "hybrid", "power"], rows),
            "PitStops": rng.integers(1, 5, rows),
            "DNFs": rng.integers(0, 3, rows),
        }
        df = pd.DataFrame(data)
        df["FinishPos"] = (0.6 * df["QualPos"] + 0.3 * (20 - df["TeamPoints"] / 600 * 10) + rng.normal(0, 2, rows)).clip(
            1, 20
        )
        return df
