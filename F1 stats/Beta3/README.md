# F1 Dashboard Beta 3

A PyQt5 desktop dashboard for Formula 1 telemetry and results. It combines FastF1 telemetry with Ergast (Jolpi) race data, provides caching to avoid repeated downloads, and offers comparison and plotting utilities.

## Features
- Dark-themed PyQt5 UI with tabs for telemetry, race results, multi-driver comparisons, and standings.
- FastF1 helpers (`fastf1_utils.py`) to load sessions, driver laps/telemetry, and basic lap comparisons.
- Ergast API helpers (`api_utils.py`) with file+memory caching for results, standings, qualifying, schedules, and driver info.
- Matplotlib plotting utilities (`plot_utils.py`) for speed traces, throttle/brake/gear overlays, lap time comparisons, deltas, tyre strategy, and cornering scatter.
- Telemetry processing (`telemetry_utils.py`) that cleans data and summarizes per-driver metrics (avg/max speed, throttle, brake usage, lap duration, gear changes).
- Simple cache validation script (`cache_dry_run.py`) to sanity-check cache expiry and clearing.

## Requirements
- Python 3.10+ recommended.
- Dependencies: `PyQt5`, `matplotlib`, `numpy`, `pandas`, `fastf1`, `requests`.

Install with:
```bash
pip install PyQt5 matplotlib numpy pandas fastf1 requests
```

FastF1 will create its own cache directory (`f1_cache/`) on first use.

## Running
From this folder:
```bash
python main.py
```
Choose a season and race, fetch results, then load telemetry or run multi-driver comparison.

## Caching
- `app_cache/`: pickled responses from API/cache manager. Safe to delete; do not commit.
- `f1_cache/`: FastF1 download cache. Safe to delete; do not commit.

## Project Layout
- `main.py`: Qt entrypoint, sets dark palette and launches the main window.
- `ui_main.py`: Main window with tabs, threading for telemetry fetch, and UI interactions.
- `api_utils.py`: Ergast/Jolpi API accessors with caching.
- `fastf1_utils.py`: FastF1 session/lap/telemetry helpers.
- `plot_utils.py`: Matplotlib plotting helpers for telemetry and comparisons.
- `telemetry_utils.py`: Cleaning and per-driver metric summaries.
- `data_cache.py`: File+memory cache manager.
- `cache_dry_run.py`: Dry-run test for cache expiry and clearing.

## Limitations
- UI season dropdown is 2024–2019; future seasons and pre-2019 arent exposed. FastF1 telemetry is generally reliable from 2018 onward; older seasons may not have full data.
- Race round mapping in `api_utils.py` is hardcoded for the 2024 calendar; future calendars need an updated mapping or a dynamic schedule fetch.

## Contributing/Testing
- To sanity-check caching without network calls, run: `python cache_dry_run.py`.
- Avoid committing cache directories (`app_cache/`, `f1_cache/`, or any `*.pkl`).
