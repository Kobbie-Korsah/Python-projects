"""
api_utils.py - Jolpica-F1 API Functions
Handles fetching historical F1 data from the Jolpica-F1 REST API
"""

import requests
import pandas as pd
import time

# Base URL for Jolpica-F1 API
BASE_URL = "https://api.jolpi.ca/ergast/f1"

def fetch_jolpica_data(season, race_number):
    """
    Fetch race results from Jolpica-F1 API (Ergast data)
    
    Parameters:
    -----------
    season : int
        The F1 season year (e.g., 2024)
    race_number : int
        The race round number in the season
    
    Returns:
    --------
    DataFrame:
        Pandas DataFrame with race results or None if error
    """
    
    print(f"\n[FETCHING] Fetching Jolpica API data for {season} Round {race_number}...")
    
    try:
        # Step 1: Construct the API endpoint URL
        # Format: https://api.jolpi.ca/ergast/f1/{season}/{race_number}/results
        url = f"{BASE_URL}/{season}/{race_number}/results"
        print(f"   API URL: {url}")
        
        # Step 2: Make GET request to API
        print(f"   Sending request...")
        response = requests.get(url, timeout=10)
        
        # Step 3: Check if request was successful (status code 200)
        if response.status_code != 200:
            print(f"   [ERROR] API request failed with status code: {response.status_code}")
            return None
        
        # Step 4: Parse JSON response
        data = response.json()
        
        # Step 5: Navigate through JSON structure to get race results
        # JSON structure: MRData -> RaceTable -> Races -> Results
        try:
            race_data = data['MRData']['RaceTable']['Races'][0]
            results = race_data['Results']
            
            # Get race metadata
            race_name = race_data['raceName']
            circuit_name = race_data['Circuit']['circuitName']
            race_date = race_data['date']
            
            print(f"   [OK] Race: {race_name}")
            print(f"   [OK] Circuit: {circuit_name}")
            print(f"   [OK] Date: {race_date}")
            print(f"   [OK] Found {len(results)} drivers")
            
        except (KeyError, IndexError) as e:
            print(f"   [ERROR] Error parsing JSON structure: {e}")
            return None
        
        # Step 6: Extract relevant fields into a list of dictionaries
        parsed_results = []
        
        for result in results:
            # Extract driver information
            driver_info = result['Driver']
            driver_name = f"{driver_info['givenName']} {driver_info['familyName']}"
            
            # Extract constructor (team) information
            constructor_name = result['Constructor']['name']
            
            # Extract race result information
            position = result['position']
            points = result['points']
            
            # Time/Status: either finish time or status (e.g., "Retired", "DNF")
            time_status = result.get('Time', {}).get('time', result.get('status', 'N/A'))
            
            # Grid position (starting position)
            grid = result['grid']
            
            # Number of laps completed
            laps = result['laps']
            
            # Append to results list
            parsed_results.append({
                'Position': position,
                'Driver': driver_name,
                'DriverCode': driver_info['code'],
                'Constructor': constructor_name,
                'Grid': grid,
                'Laps': laps,
                'Time': time_status,
                'Points': points
            })
        
        # Step 7: Convert list of dictionaries to pandas DataFrame
        df = pd.DataFrame(parsed_results)
        
        print(f"   [OK] Successfully parsed race results into DataFrame")
        return df
    
    except requests.exceptions.Timeout:
        print(f"   [ERROR] Request timed out")
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"   [ERROR] Request error: {e}")
        return None
    
    except Exception as e:
        print(f"   [ERROR] Unexpected error: {e}")
        return None

def fetch_driver_standings(season):
    """
    Fetch driver championship standings for a season
    
    Parameters:
    -----------
    season : int
        The F1 season year
    
    Returns:
    --------
    DataFrame:
        Pandas DataFrame with driver standings
    """
    
    print(f"\n[FETCHING] Fetching driver standings for {season}...")
    
    try:
        # Construct URL for driver standings
        url = f"{BASE_URL}/{season}/driverStandings"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"   [ERROR] Failed to fetch standings (status: {response.status_code})")
            return None
        
        data = response.json()
        standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
        
        # Parse standings data
        parsed_standings = []
        for driver in standings:
            driver_info = driver['Driver']
            parsed_standings.append({
                'Position': driver['position'],
                'Driver': f"{driver_info['givenName']} {driver_info['familyName']}",
                'Constructor': driver['Constructors'][0]['name'],
                'Points': driver['points'],
                'Wins': driver['wins']
            })
        
        df = pd.DataFrame(parsed_standings)
        print(f"   [OK] Successfully fetched {len(df)} driver standings")
        
        return df
    
    except Exception as e:
        print(f"   ❌ Error fetching standings: {e}")
        return None

def get_race_schedule(season):
    """
    Get the race schedule/calendar for a season
    
    Parameters:
    -----------
    season : int
        The F1 season year
    
    Returns:
    --------
    DataFrame:
        Pandas DataFrame with race schedule
    """
    
    try:
        url = f"{BASE_URL}/{season}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        races = data['MRData']['RaceTable']['Races']
        
        schedule = []
        for race in races:
            schedule.append({
                'Round': race['round'],
                'RaceName': race['raceName'],
                'Circuit': race['Circuit']['circuitName'],
                'Location': race['Circuit']['Location']['locality'],
                'Country': race['Circuit']['Location']['country'],
                'Date': race['date']
            })
        
        return pd.DataFrame(schedule)
    
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return None