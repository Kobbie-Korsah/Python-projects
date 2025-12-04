# ApexAnalytics

Professional PyQt6 desktop application for Formula 1 analytics, telemetry visualization, and basic machine learning predictions.

## Highlights
- Multi-tab UI with Driver/Team mode toggle, season/race selectors, and dark F1 styling (`styles.qss`).
- Driver Hub: profiles, career stats, constructor history, season charts, photo support from `assets/logos/drivers`.
- Team Hub: logos, standings, results, and strategy views for each constructor.
- Telemetry: lap traces (speed, throttle, brake, gear) via FastF1 with smoothing and hover helpers.
- Comparison: head-to-head telemetry and lap time deltas for 2-3 drivers.
- Analytics: pace consistency, tyre strategy, and performance metrics.
- ML Predictor: simple model training and feature-importance visualization.
- Caching and background workers for responsive API/telemetry calls; export hooks for modules that implement `export_data`.

## Project Structure
- `main.py` - entry point, dark palette, loads the main window and stylesheet.
- `ui_main.py` - main window with tabs, mode switcher, menu actions (export, clear cache, about).
- `core/` - caching (`data_cache.py`), threading workers (`threading.py`), shared enums/constants (`enums.py`).
- `modules/` - feature tabs: `driver_hub.py`, `team_hub.py`, `telemetry.py`, `comparison.py`, `analytics.py`, `ml_predictor.py`.
- `utils/` - data fetching, plotting, and UI helpers (`fastf1_utils.py`, `api_utils.py`, `plot_utils.py`, `ui_helpers.py`).
- `assets/` - provide your own images: `logos/drivers/VER.png`, `logos/teams/ferrari.png`, etc.
- Runtime folders (auto-created): `cache/`, `fastf1_cache/`, `logs/`, `__pycache__/`.
- Docs/styles: `SETUP.md`, `PROJECT_STRUCTURE.md`, `styles.qss` (Qt stylesheet), `styles.css` copy.

## Setup
1. Python 3.9+ and `pip`. Recommended: virtual environment.
2. Install dependencies (requirements.txt not present, use command below):
   ```
   pip install PyQt6 fastf1 matplotlib pandas numpy requests scikit-learn scipy pillow
   ```
3. Add assets you own:
   - Driver photos -> `assets/logos/drivers/VER.png`, `HAM.png`, etc. (about 200x200).
   - Team logos -> `assets/logos/teams/ferrari.png`, `red_bull_racing.png`, etc.
4. Run the app:
   ```
   python main.py
   ```
   Use Tools -> Clear Cache to reset cached API/telemetry data.

## Data Sources and Caching
- FastF1 provides telemetry; Jolpica/Ergast API provides results and standings (see `core/enums.py`).
- Cached responses live in `fastf1_cache/` (FastF1) and `cache/` (app pickle cache). Both can be deleted safely; they will repopulate.
- Logs are written to `logs/error.log` via the global exception hook.

## Exporting
Modules that implement `export_data` can be exported through File -> "Export Current View". Driver/Team modules also expose PNG/CSV/JSON hooks where implemented.

## What to Commit (GitHub)
- Include: `*.py`, `styles.qss`, `styles.css`, `SETUP.md`, `PROJECT_STRUCTURE.md`, and this README.
- Include if licensed: any custom assets you created and have rights to share.
- Exclude: `fastf1_cache/`, `cache/`, `logs/`, `__pycache__/`, `*.pyc`, `*.pkl`, `.DS_Store`.
- Exclude: virtualenvs (`venv/`, `.venv/`) and large downloads.
- Exclude copyrighted photos/logos unless you have redistribution rights (keep them local otherwise).

Recommended `.gitignore`:
```
venv/
.venv/
__pycache__/
*.pyc
*.pkl
.cache/
cache/
fastf1_cache/
logs/
*.log
.DS_Store
```

## Troubleshooting
- `ModuleNotFoundError: PyQt6` -> install dependencies command above.
- Telemetry/API failures -> verify internet access, correct race name, then clear `fastf1_cache/` and `cache/`.
- Missing images -> ensure files exist in `assets/logos/...` with exact names/codes.
