
import fastf1
import pandas as pd
import os

# Enable FastF1 caching to improve performance and reduce API calls
CACHE_DIR = "cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
fastf1.Cache.enable_cache(CACHE_DIR)

def fetch_fastf1_data(season, race_number, driver_code):
    """
    Fetch fastest lap data for a specific driver in a race using FastF1
    
    Parameters:
    -----------
    season : int
        The F1 season year (e.g., 2024)
    race_number : int
        The race round number in the season (1-24)
    driver_code : str
        Three-letter driver code (e.g., 'VER', 'HAM', 'LEC')
    
    Returns:
    --------
    dict:
        Dictionary containing fastest lap data or None if error
    """
    
    print(f"\n[FETCHING] Fetching FastF1 data for {driver_code}...")
    
    try:
        # Step 1: Load the race session
        # 'R' = Race, 'Q' = Qualifying, 'FP1/FP2/FP3' = Free Practice
        print(f"   Loading session: {season} Round {race_number} (Race)")
        session = fastf1.get_session(season, race_number, 'R')
        
        # Step 2: Load session data (laps, telemetry, etc.)
        print(f"   Loading session data...")
        session.load()
        
        # Step 3: Get all laps for the specified driver
        driver_laps = session.laps.pick_driver(driver_code)
        
        if driver_laps.empty:
            print(f"   [ERROR] No lap data found for driver {driver_code}")
            return None
        
        # Step 4: Pick the fastest lap from all driver laps
        fastest_lap = driver_laps.pick_fastest()
        
        if fastest_lap is None or fastest_lap.empty:
            print(f"   [ERROR] No fastest lap found for {driver_code}")
            return None
        
        # Step 5: Extract relevant data from the fastest lap
        # Convert lap time to string format for better readability
        lap_time_str = str(fastest_lap['LapTime']).split()[-1] if pd.notna(fastest_lap['LapTime']) else "N/A"
        
        fastest_lap_data = {
            'Driver': fastest_lap['Driver'],
            'Team': fastest_lap['Team'],
            'LapTime': lap_time_str,
            'LapNumber': int(fastest_lap['LapNumber']),
            'Compound': fastest_lap['Compound'],  # Tire compound (SOFT, MEDIUM, HARD)
            'TyreLife': int(fastest_lap['TyreLife']),  # Age of tires in laps
            'SpeedI1': round(fastest_lap['SpeedI1'], 2) if pd.notna(fastest_lap['SpeedI1']) else 0,
            'SpeedI2': round(fastest_lap['SpeedI2'], 2) if pd.notna(fastest_lap['SpeedI2']) else 0,
            'SpeedFL': round(fastest_lap['SpeedFL'], 2) if pd.notna(fastest_lap['SpeedFL']) else 0,
            'SpeedST': round(fastest_lap['SpeedST'], 2) if pd.notna(fastest_lap['SpeedST']) else 0,
        }
        
        print(f"   [OK] Successfully fetched fastest lap data")
        return fastest_lap_data
    
    except Exception as e:
        print(f"   [ERROR] Error in fetch_fastf1_data: {e}")
        return None

def save_to_csv(data, filename):
    """
    Save data dictionary to CSV file
    
    Parameters:
    -----------
    data : dict
        Dictionary containing data to save
    filename : str
        Path and filename for the CSV file
    """
    
    try:
        # Convert dictionary to DataFrame for easy CSV export
        df = pd.DataFrame([data])
        
        # Save to CSV without index column
        df.to_csv(filename, index=False)
        
        return True
    
    except Exception as e:
        print(f"   [ERROR] Error saving to CSV: {e}")
        return False

def get_session_info(season, race_number):
    """
    Get basic information about a race session
    
    Parameters:
    -----------
    season : int
        The F1 season year
    race_number : int
        The race round number
    
    Returns:
    --------
    dict : Dictionary with session metadata
    """
    
    try:
        session = fastf1.get_session(season, race_number, 'R')
        session.load()
        
        session_info = {
            'EventName': session.event['EventName'],
            'Location': session.event['Location'],
            'Country': session.event['Country'],
            'EventDate': str(session.event['EventDate']),
        }
        
        return session_info
    
    except Exception as e:
        print(f"Error getting session info: {e}")
        return None