# F1 Dashboard Beta 2 (PyQt5 UI)

GUI prototype adding a Qt front end, tables, and charts on top of FastF1 + Ergast data.

## Features
- PyQt5 window with controls to select season, race, and driver.
- Background thread fetches FastF1 session + driver laps and Ergast race results.
- Lap time chart embedded via Matplotlib (`plot_utils.py`).
- Results table populated from Ergast/Jolpi API data.
- Buttons to load/save results CSVs and export screenshots (see UI for options).

## Files
- `main.py` — Qt entrypoint that creates `QApplication` and shows `F1DashboardWindow`.
- `ui_main.py` — Main window layout, controls, threading, and callbacks to fetch data and update the table/plot.
- `fastf1_utils.py` — FastF1 helpers to load sessions and driver laps (enables `cache/`).
- `api_utils.py` — Ergast/Jolpi helpers for race results with basic parsing.
- `plot_utils.py` — Matplotlib helper to plot lap times.
- `qt_debug.txt` / `error.txt` — empty placeholders from Qt debug/output.

## Requirements
- Python 3.10+ recommended.
- Dependencies: `PyQt5`, `matplotlib`, `pandas`, `fastf1`, `requests`.

Install:
```bash
pip install PyQt5 matplotlib pandas fastf1 requests
```

## Running
From this folder:
```bash
python main.py
```
Select season/race/driver, then trigger the fetch; results populate the table and chart.

## Caching & Artifacts
- `cache/`: FastF1 download cache (auto-created). Do not commit; safe to delete.
- `__pycache__/`: Python bytecode. Do not commit; safe to delete.

## Notes
- Race selection expects Ergast naming; future/older seasons may need schedule tweaks.
- Threading is minimal; long fetches may still feel blocking on slow networks.
