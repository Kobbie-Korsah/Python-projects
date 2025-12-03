# F1 Analytics Dashboard

A multi-threaded PyQt6 application combining FastF1 telemetry with Jolpica F1 API metadata. Tabs include Driver Hub, Team Hub, Telemetry, Comparison, Analytics, Historical Lens, ML Predictor, and constructor/export utilities.

## Features
- Background workers for all data fetching to keep UI responsive.
- Driver and team hubs powered by Jolpica + FastF1.
- Telemetry viewer with speed trace plotting.
- Driver vs driver comparison and race pace analytics.
- Historical trajectories for drivers or constructors.
- ML predictor using RandomForestRegressor on synthetic season stats.
- Export support for CSV/JSON/PNG/Markdown in relevant modules.

## Setup
1. Create/activate a venv and install requirements:
   ```bash
   pip install PyQt6 fastf1 matplotlib pandas scikit-learn requests
   ```
2. (Optional) Set your Jolpica API key via environment variable:
   ```bash
   set JOLPICA_API_KEY=your_key_here  # Windows
   export JOLPICA_API_KEY=your_key_here  # macOS/Linux
   ```

## Running
```bash
python main.py
```

## Notes
- FastF1 will use a local `cache/` directory; ensure it is writable.
- Network calls are wrapped; in offline environments you can still explore the UI and synthetic ML predictor.
