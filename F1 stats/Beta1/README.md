# F1 Dashboard Beta 1 (Console)

Console-only prototype for fetching Formula 1 data.
- Uses FastF1 to load a race session and report a driver’s fastest lap.
- Uses Ergast (Jolpi) API to pull race results and save to CSV.
- Writes outputs to `output/` and caches FastF1 downloads in `cache/`.

## Files
- `main.py` — CLI flow: set season/race/driver constants, fetch fastest lap, print and save CSV; then fetch race results and save CSV.
- `fastf1_utils.py` — FastF1 helpers to load a session, pick the fastest lap for a driver, and save dicts to CSV. Enables local cache in `cache/`.
- `api_utils.py` — Ergast/Jolpi helpers for race results, standings, and schedule retrieval.

## Requirements
- Python 3.10+ recommended.
- Dependencies: `fastf1`, `pandas`, `requests`.

Install:
```bash
pip install fastf1 pandas requests
```

## Running
From this folder:
```bash
python main.py
```
Edit `SEASON`, `RACE_NUMBER`, and `DRIVER_CODE` in `main.py` to change targets.

## Outputs & Caching
- CSVs land in `output/`.
- FastF1 cache in `cache/` (auto-created); safe to delete, do not commit.

## Notes
- Race selection is hardcoded to round numbers; update `RACE_NUMBER` for different rounds.
- Telemetry depth is minimal (fastest lap only) and only in the console.
- See `race_rounds_2019_2024.md` for round-to-race mappings for 2019–2024.
