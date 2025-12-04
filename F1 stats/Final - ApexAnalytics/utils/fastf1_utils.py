"""
F1 Analytics Suite - FastF1 Utilities
Complete FastF1 integration with caching and error handling
"""

from pathlib import Path

import fastf1
import pandas as pd
import numpy as np
from datetime import timedelta
from typing import Optional, List, Dict, Tuple
from core.data_cache import get_cache

# Enable FastF1 caching for faster repeated loads
# Use an absolute path so running from other working directories still works
CACHE_DIR = Path(__file__).resolve().parent.parent / 'fastf1_cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

def fetch_session_data(year: int, race: str, session_type: str = 'R'):
    """
    Fetch F1 session data with caching
    
    Args:
        year: Season year
        race: Race name or round number
        session_type: 'R' (Race), 'Q' (Qualifying), 'FP1', 'FP2', 'FP3', 'S' (Sprint)
    
    Returns:
        fastf1.core.Session: Loaded session object
    """
    cache = get_cache()
    cache_key = f"session_{year}_{race}_{session_type}"
    
    # Check cache
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Fetch fresh data
    try:
        session = fastf1.get_session(year, race, session_type)
        session.load()
        
        # Cache the session
        cache.set(cache_key, session)
        return session
    except Exception as e:
        raise Exception(f"Failed to load session: {str(e)}")

def fetch_driver_laps(session, driver_code: str) -> pd.DataFrame:
    """
    Fetch all laps for a specific driver
    
    Args:
        session: FastF1 session object
        driver_code: Three-letter driver code (e.g., 'VER')
    
    Returns:
        pd.DataFrame: Lap data
    """
    try:
        driver_laps = session.laps.pick_driver(driver_code)
        
        if driver_laps.empty:
            return pd.DataFrame()
        
        # Select relevant columns
        relevant_cols = ['LapNumber', 'LapTime', 'Compound', 'TyreLife', 
                        'Stint', 'TrackStatus', 'IsPersonalBest', 'Sector1Time',
                        'Sector2Time', 'Sector3Time']
        
        # Filter to columns that exist
        available_cols = [col for col in relevant_cols if col in driver_laps.columns]
        
        return driver_laps[available_cols].copy()
    except Exception as e:
        print(f"Error fetching laps for {driver_code}: {e}")
        return pd.DataFrame()

def fetch_driver_telemetry(session, driver_code: str, lap_type: str = 'fastest') -> pd.DataFrame:
    """
    Fetch telemetry data for a driver's lap
    
    Args:
        session: FastF1 session object
        driver_code: Three-letter driver code
        lap_type: 'fastest', 'average', or 'first'
    
    Returns:
        pd.DataFrame: Telemetry data (Speed, Throttle, Brake, Gear, RPM, etc.)
    """
    try:
        driver_laps = session.laps.pick_driver(driver_code)
        
        if driver_laps.empty:
            return pd.DataFrame()
        
        # Select lap based on type
        if lap_type == 'fastest':
            lap = driver_laps.pick_fastest()
        elif lap_type == 'first':
            lap = driver_laps.iloc[0]
        else:  # average
            median_idx = len(driver_laps) // 2
            lap = driver_laps.iloc[median_idx]
        
        # Get telemetry
        telemetry = lap.get_telemetry()
        
        # Add calculated fields
        if not telemetry.empty:
            telemetry['DistanceDelta'] = telemetry['Distance'].diff().fillna(0)
            
            if 'Speed' in telemetry.columns:
                telemetry['Acceleration'] = telemetry['Speed'].diff().fillna(0)
        
        return telemetry
    except Exception as e:
        print(f"Error fetching telemetry for {driver_code}: {e}")
        return pd.DataFrame()

def get_fastest_lap_info(session, driver_code: str) -> Dict:
    """
    Get fastest lap information for a driver
    
    Args:
        session: FastF1 session object
        driver_code: Driver code
    
    Returns:
        Dict: Fastest lap information
    """
    try:
        driver_laps = session.laps.pick_driver(driver_code)
        
        if driver_laps.empty:
            return {}
        
        fastest = driver_laps.pick_fastest()
        
        return {
            'lap_number': int(fastest['LapNumber']),
            'lap_time': fastest['LapTime'].total_seconds() if pd.notna(fastest['LapTime']) else None,
            'compound': fastest.get('Compound', 'Unknown'),
            'tyre_life': int(fastest['TyreLife']) if pd.notna(fastest.get('TyreLife')) else None,
            'sector1': fastest['Sector1Time'].total_seconds() if pd.notna(fastest.get('Sector1Time')) else None,
            'sector2': fastest['Sector2Time'].total_seconds() if pd.notna(fastest.get('Sector2Time')) else None,
            'sector3': fastest['Sector3Time'].total_seconds() if pd.notna(fastest.get('Sector3Time')) else None,
        }
    except Exception as e:
        print(f"Error getting fastest lap for {driver_code}: {e}")
        return {}

def get_pit_stops(session, driver_code: str) -> pd.DataFrame:
    """
    Get pit stop data for a driver
    
    Args:
        session: FastF1 session object
        driver_code: Driver code
    
    Returns:
        pd.DataFrame: Pit stop data
    """
    try:
        driver_laps = session.laps.pick_driver(driver_code)
        
        if driver_laps.empty:
            return pd.DataFrame()
        
        # Find laps where pit stops occurred
        pit_laps = driver_laps[driver_laps['PitOutTime'].notna()]
        
        return pit_laps[['LapNumber', 'PitInTime', 'PitOutTime', 'Compound']].copy()
    except Exception as e:
        print(f"Error getting pit stops for {driver_code}: {e}")
        return pd.DataFrame()

def get_tyre_strategy(session, driver_code: str) -> List[Dict]:
    """
    Get tyre strategy (stints) for a driver
    
    Args:
        session: FastF1 session object
        driver_code: Driver code
    
    Returns:
        List[Dict]: Tyre strategy by stint
    """
    try:
        driver_laps = session.laps.pick_driver(driver_code)
        
        if driver_laps.empty:
            return []
        
        strategy = []
        
        for stint in driver_laps['Stint'].unique():
            stint_laps = driver_laps[driver_laps['Stint'] == stint]
            
            if not stint_laps.empty:
                strategy.append({
                    'stint': int(stint),
                    'compound': stint_laps.iloc[0]['Compound'],
                    'start_lap': int(stint_laps['LapNumber'].min()),
                    'end_lap': int(stint_laps['LapNumber'].max()),
                    'total_laps': len(stint_laps),
                    'avg_lap_time': stint_laps['LapTime'].mean().total_seconds() if pd.notna(stint_laps['LapTime'].mean()) else None
                })
        
        return strategy
    except Exception as e:
        print(f"Error getting tyre strategy for {driver_code}: {e}")
        return []

def get_position_changes(session, driver_code: str) -> pd.DataFrame:
    """
    Get position changes throughout the race
    
    Args:
        session: FastF1 session object
        driver_code: Driver code
    
    Returns:
        pd.DataFrame: Position by lap
    """
    try:
        driver_laps = session.laps.pick_driver(driver_code)
        
        if driver_laps.empty:
            return pd.DataFrame()
        
        return driver_laps[['LapNumber', 'Position']].copy()
    except Exception as e:
        print(f"Error getting position changes for {driver_code}: {e}")
        return pd.DataFrame()

def calculate_pace_consistency(session, driver_code: str) -> Dict:
    """
    Calculate race pace consistency metrics
    
    Args:
        session: FastF1 session object
        driver_code: Driver code
    
    Returns:
        Dict: Consistency metrics
    """
    try:
        driver_laps = session.laps.pick_driver(driver_code)
        
        if driver_laps.empty:
            return {}
        
        # Filter valid laps (exclude in/out laps, safety car, etc.)
        valid_laps = driver_laps[
            (driver_laps['PitInTime'].isna()) & 
            (driver_laps['PitOutTime'].isna()) &
            (driver_laps['TrackStatus'] == '1')
        ]
        
        if valid_laps.empty:
            return {}
        
        lap_times = valid_laps['LapTime'].dropna()
        lap_times_seconds = lap_times.dt.total_seconds()
        
        return {
            'mean_lap_time': lap_times_seconds.mean(),
            'std_dev': lap_times_seconds.std(),
            'fastest_lap': lap_times_seconds.min(),
            'slowest_lap': lap_times_seconds.max(),
            'consistency_score': 100 - (lap_times_seconds.std() / lap_times_seconds.mean() * 100),
            'total_laps': len(valid_laps)
        }
    except Exception as e:
        print(f"Error calculating pace consistency for {driver_code}: {e}")
        return {}

def get_weather_data(session) -> Dict:
    """
    Get weather data for the session
    
    Args:
        session: FastF1 session object
    
    Returns:
        Dict: Weather information
    """
    try:
        weather = session.weather_data
        
        if weather.empty:
            return {}
        
        # Get average conditions
        return {
            'avg_air_temp': weather['AirTemp'].mean(),
            'avg_track_temp': weather['TrackTemp'].mean(),
            'avg_humidity': weather['Humidity'].mean(),
            'avg_pressure': weather['Pressure'].mean(),
            'rainfall': weather['Rainfall'].any()
        }
    except Exception as e:
        print(f"Error getting weather data: {e}")
        return {}

def compare_driver_telemetry(session, driver1: str, driver2: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Get telemetry for two drivers for comparison
    
    Args:
        session: FastF1 session object
        driver1: First driver code
        driver2: Second driver code
    
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Telemetry for both drivers
    """
    telem1 = fetch_driver_telemetry(session, driver1, 'fastest')
    telem2 = fetch_driver_telemetry(session, driver2, 'fastest')
    
    return telem1, telem2

def get_session_results(session) -> pd.DataFrame:
    """
    Get final session results
    
    Args:
        session: FastF1 session object
    
    Returns:
        pd.DataFrame: Results table
    """
    try:
        results = session.results
        
        if results.empty:
            return pd.DataFrame()
        
        # Select relevant columns
        relevant_cols = ['Position', 'Abbreviation', 'FullName', 'TeamName', 
                        'GridPosition', 'Points', 'Status', 'Time']
        
        available_cols = [col for col in relevant_cols if col in results.columns]
        
        return results[available_cols].copy()
    except Exception as e:
        print(f"Error getting session results: {e}")
        return pd.DataFrame()

def apply_savgol_filter(data: pd.Series, window: int = 15, poly: int = 3) -> pd.Series:
    """
    Apply Savitzky-Golay filter for smoothing
    
    Args:
        data: Data series to smooth
        window: Window size
        poly: Polynomial order
    
    Returns:
        pd.Series: Smoothed data
    """
    from scipy.signal import savgol_filter
    
    try:
        if len(data) < window:
            return data
        
        smoothed = savgol_filter(data, window, poly)
        return pd.Series(smoothed, index=data.index)
    except Exception as e:
        print(f"Error applying Savgol filter: {e}")
        return data
