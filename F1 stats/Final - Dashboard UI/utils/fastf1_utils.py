"""
Helper functions for interacting with FastF1 data and building telemetry frames.
These functions should be executed inside Worker threads.
"""

from typing import Any, Dict, Optional, Tuple

import fastf1
import pandas as pd
from fastf1.core import Laps, Session


def load_session(season: int, round_no: int, session_name: str) -> Optional[Session]:
    """Load a FastF1 session with caching enabled."""
    try:
        fastf1.Cache.enable_cache("cache")
        return fastf1.get_session(season, round_no, session_name)
    except Exception:
        return None


def get_laps(session: Session) -> Laps:
    """Return laps; caller should ensure session.load() has been called."""
    return session.load().laps


def build_driver_telemetry(session: Session, driver: str) -> pd.DataFrame:
    """
    Build a telemetry dataframe with smoothing for speed and throttle traces.
    """
    session.load()
    laps = session.laps.pick_driver(driver)
    fastest = laps.pick_fastest()
    telemetry = fastest.get_car_data().add_distance()
    telemetry["ThrottleSmooth"] = telemetry["Throttle"].rolling(5, center=True).mean()
    telemetry["BrakeSmooth"] = telemetry["Brake"].rolling(5, center=True).mean()
    return telemetry


def compare_lap_delta(session: Session, driver_a: str, driver_b: str) -> Tuple[pd.Series, pd.Series]:
    """Return distance-aligned speed traces for two drivers."""
    session.load()
    lap_a = session.laps.pick_driver(driver_a).pick_fastest().get_car_data().add_distance()
    lap_b = session.laps.pick_driver(driver_b).pick_fastest().get_car_data().add_distance()
    merged = lap_a.merge(lap_b, on="Distance", suffixes=("_a", "_b"))
    return merged["Speed_a"], merged["Speed_b"]


def pit_stop_summary(session: Session) -> pd.DataFrame:
    """Return pit stop times per driver."""
    session.load()
    stops = session.laps[session.laps["PitOutTime"].notna()]
    grouped = stops.groupby("Driver")["PitInTime"].count().reset_index(name="Stops")
    return grouped
