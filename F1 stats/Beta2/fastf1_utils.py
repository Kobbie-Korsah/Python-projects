"""
F1 Dashboard Beta 2 - FastF1 Utilities
Fetch session data and driver telemetry using FastF1
"""
import fastf1
import pandas as pd
import os

# Enable cache for faster subsequent loads
CACHE_DIR = 'cache'
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
fastf1.Cache.enable_cache(CACHE_DIR)

def fetch_session_data(year, race_name):
    """
    Fetch F1 session data for a given year and race
    
    Args:
        year (int): Season year (e.g., 2024)
        race_name (str): Race name (e.g., "Bahrain")
    
    Returns:
        fastf1.core.Session: Loaded session object
    """
    # FastF1 expects a round identifier (usually an int) for the session.
    # Accept common race names from the UI and map them to round numbers.
    race_map = {
        "Bahrain": 1, "Saudi Arabia": 2, "Australia": 3, "Japan": 4, "China": 5,
        "Miami": 6, "Emilia Romagna": 7, "Monaco": 8, "Canada": 9, "Spain": 10,
        "Austria": 11, "Great Britain": 12, "Hungary": 13, "Belgium": 14,
        "Netherlands": 15, "Italy": 16, "Azerbaijan": 17, "Singapore": 18,
        "United States": 19, "Mexico": 20, "Brazil": 21, "Las Vegas": 22,
        "Qatar": 23, "Abu Dhabi": 24
    }

    round_id = race_map.get(race_name, None)
    if round_id is None:
        # If not found, try to pass the race_name directly (FastF1 may accept round strings)
        round_id = race_name

    try:
        # Load the race session (Race = main race, not qualifying or practice)
        session = fastf1.get_session(year, round_id, 'R')
        session.load()
        return session
    except Exception as e:
        print(f"[ERROR] Failed to load FastF1 session for {year} {race_name}: {e}")
        return None

def fetch_driver_laps(session, driver_code):
    """
    Fetch all laps for a specific driver in a session
    
    Args:
        session (fastf1.core.Session): Loaded session
        driver_code (str): Three-letter driver code (e.g., "VER")
    
    Returns:
        pd.DataFrame: DataFrame containing lap data
    """
    # Get laps for the specified driver
    driver_laps = session.laps.pick_driver(driver_code)
    
    # Return as DataFrame with relevant columns
    return driver_laps[['LapNumber', 'LapTime', 'Compound', 'TyreLife', 
                         'Stint', 'TrackStatus', 'IsPersonalBest']].copy()

def get_fastest_lap(session):
    """
    Get the fastest lap of the session
    
    Args:
        session (fastf1.core.Session): Loaded session
    
    Returns:
        fastf1.core.Lap: Fastest lap object
    """
    return session.laps.pick_fastest()

def get_driver_telemetry(session, driver_code, lap_number=None):
    """
    Fetch telemetry data for a driver
    
    Args:
        session (fastf1.core.Session): Loaded session
        driver_code (str): Three-letter driver code
        lap_number (int, optional): Specific lap number. If None, gets fastest lap
    
    Returns:
        pd.DataFrame: Telemetry data (Speed, Throttle, Brake, RPM, etc.)
    """
    driver_laps = session.laps.pick_driver(driver_code)
    
    if lap_number:
        lap = driver_laps[driver_laps['LapNumber'] == lap_number].iloc[0]
    else:
        # Get fastest lap
        lap = driver_laps.pick_fastest()
    
    return lap.get_telemetry()

def get_session_results(session):
    """
    Get final race results from session
    
    Args:
        session (fastf1.core.Session): Loaded session
    
    Returns:
        pd.DataFrame: Results with position, driver, team, points
    """
    return session.results[['Position', 'Abbreviation', 'TeamName', 'Points', 'Status']]