"""
F1 Dashboard Beta 3 - FastF1 Utilities
Enhanced telemetry fetching with caching
"""
import fastf1
import pandas as pd
import os
from pathlib import Path
from data_cache import CacheManager

# Create and enable FastF1 caching
cache_dir = Path('f1_cache')
cache_dir.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(cache_dir))

cache_manager = CacheManager()

def fetch_session_data(year, race_name):
    """
    Fetch F1 session data with caching
    
    Args:
        year (int): Season year
        race_name (str): Race name
    
    Returns:
        fastf1.core.Session: Loaded session
    """
    cache_key = f"session_{year}_{race_name}"
    
    # Check cache
    cached = cache_manager.get(cache_key)
    if cached:
        return cached
    
    # Fetch fresh data
    session = fastf1.get_session(year, race_name, 'R')
    session.load()
    
    # Cache it
    cache_manager.set(cache_key, session)
    
    return session

def fetch_driver_laps(session, driver_code):
    """
    Fetch all laps for a driver
    
    Args:
        session: FastF1 session
        driver_code (str): Three-letter driver code
    
    Returns:
        pd.DataFrame: Lap data
    """
    driver_laps = session.laps.pick_driver(driver_code)
    
    if driver_laps.empty:
        return pd.DataFrame()
    
    return driver_laps[['LapNumber', 'LapTime', 'Compound', 'TyreLife',
                         'Stint', 'TrackStatus', 'IsPersonalBest']].copy()

def fetch_driver_telemetry(session, driver_code, lap_type='fastest'):
    """
    Fetch telemetry data for a specific driver
    
    Args:
        session: FastF1 session
        driver_code (str): Driver code
        lap_type (str): 'fastest', 'average', 'first'
    
    Returns:
        pd.DataFrame: Telemetry data (Speed, Throttle, Brake, Gear, RPM, etc.)
    """
    driver_laps = session.laps.pick_driver(driver_code)
    
    if driver_laps.empty:
        return pd.DataFrame()
    
    # Select lap based on type
    if lap_type == 'fastest_lap' or lap_type == 'fastest':
        try:
            lap = driver_laps.pick_fastest()
        except:
            lap = driver_laps.iloc[0]
    elif lap_type == 'first_lap' or lap_type == 'first':
        lap = driver_laps.iloc[0]
    else:  # average
        median_idx = len(driver_laps) // 2
        lap = driver_laps.iloc[median_idx]
    
    # Get telemetry
    telemetry = lap.get_telemetry()
    
    return telemetry

def get_fastest_lap_data(session, driver_code):
    """
    Get fastest lap with full telemetry
    
    Args:
        session: FastF1 session
        driver_code (str): Driver code
    
    Returns:
        dict: {'lap': Lap object, 'telemetry': DataFrame, 'time': timedelta}
    """
    driver_laps = session.laps.pick_driver(driver_code)
    
    if driver_laps.empty:
        return None
    
    fastest_lap = driver_laps.pick_fastest()
    telemetry = fastest_lap.get_telemetry()
    
    return {
        'lap': fastest_lap,
        'telemetry': telemetry,
        'time': fastest_lap['LapTime']
    }

def get_lap_by_number(session, driver_code, lap_number):
    """
    Get specific lap by number
    
    Args:
        session: FastF1 session
        driver_code (str): Driver code
        lap_number (int): Lap number
    
    Returns:
        pd.DataFrame: Telemetry for that lap
    """
    driver_laps = session.laps.pick_driver(driver_code)
    
    if driver_laps.empty:
        return pd.DataFrame()
    
    lap = driver_laps[driver_laps['LapNumber'] == lap_number].iloc[0]
    return lap.get_telemetry()

def get_session_fastest_lap(session):
    """
    Get the overall fastest lap of the session
    
    Args:
        session: FastF1 session
    
    Returns:
        fastf1.core.Lap: Fastest lap
    """
    return session.laps.pick_fastest()

def get_driver_race_pace(session, driver_code):
    """
    Calculate average race pace (excluding outliers)
    
    Args:
        session: FastF1 session
        driver_code (str): Driver code
    
    Returns:
        float: Average lap time in seconds
    """
    driver_laps = session.laps.pick_driver(driver_code)
    
    if driver_laps.empty:
        return 0.0
    
    # Remove slow laps (pit stops, safety car, etc.)
    valid_laps = driver_laps[driver_laps['LapTime'].notna()]
    
    if valid_laps.empty:
        return 0.0
    
    # Calculate average
    avg_time = valid_laps['LapTime'].mean()
    return avg_time.total_seconds()

def compare_driver_laps(session, driver1, driver2):
    """
    Compare lap times between two drivers
    
    Args:
        session: FastF1 session
        driver1 (str): First driver code
        driver2 (str): Second driver code
    
    Returns:
        dict: Comparison data
    """
    laps1 = fetch_driver_laps(session, driver1)
    laps2 = fetch_driver_laps(session, driver2)
    
    if laps1.empty or laps2.empty:
        return None
    
    fastest1 = laps1['LapTime'].min()
    fastest2 = laps2['LapTime'].min()
    
    return {
        'driver1': driver1,
        'driver2': driver2,
        'fastest1': fastest1,
        'fastest2': fastest2,
        'delta': (fastest1 - fastest2).total_seconds(),
        'laps1': laps1,
        'laps2': laps2
    }