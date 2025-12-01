"""
F1 Dashboard Beta 2 - Jolpica-F1 API Utilities
Fetch race results and standings from Jolpica-F1 API
"""
import requests
from typing import List, Dict, Optional

# Base URL for Jolpica-F1 API
BASE_URL = "https://api.jolpi.ca/ergast/f1"

def fetch_race_results(year: int, race_name: str) -> List[Dict]:
    """
    Fetch race results for a specific race
    
    Args:
        year (int): Season year
        race_name (str): Race name (e.g., "Bahrain")
    
    Returns:
        List[Dict]: List of race results with position, driver, constructor, etc.
    """
    # Map common race names to round numbers (approximate mapping)
    race_map = {
        "Bahrain": 1, "Saudi Arabia": 2, "Australia": 3, "Japan": 4, "China": 5,
        "Miami": 6, "Emilia Romagna": 7, "Monaco": 8, "Canada": 9, "Spain": 10,
        "Austria": 11, "Great Britain": 12, "Hungary": 13, "Belgium": 14,
        "Netherlands": 15, "Italy": 16, "Azerbaijan": 17, "Singapore": 18,
        "United States": 19, "Mexico": 20, "Brazil": 21, "Las Vegas": 22,
        "Qatar": 23, "Abu Dhabi": 24
    }
    
    round_number = race_map.get(race_name, 1)
    
    # Construct API endpoint
    url = f"{BASE_URL}/{year}/{round_number}/results.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
        
        if not races:
            return []
        
        results = races[0].get('Results', [])
        
        # Format results for table display
        formatted_results = []
        for result in results:
            formatted_results.append({
                'position': result.get('position', 'N/A'),
                'driver': f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                'constructor': result['Constructor']['name'],
                'points': result.get('points', '0'),
                'status': result.get('status', 'N/A')
            })
        
        return formatted_results
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []

def fetch_driver_standings(year: int, round_number: Optional[int] = None) -> List[Dict]:
    """
    Fetch driver championship standings
    
    Args:
        year (int): Season year
        round_number (int, optional): Specific round. If None, gets final standings
    
    Returns:
        List[Dict]: Driver standings
    """
    if round_number:
        url = f"{BASE_URL}/{year}/{round_number}/driverStandings.json"
    else:
        url = f"{BASE_URL}/{year}/driverStandings.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        standings_lists = data.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
        
        if not standings_lists:
            return []
        
        standings = standings_lists[0].get('DriverStandings', [])
        
        formatted_standings = []
        for standing in standings:
            formatted_standings.append({
                'position': standing.get('position', 'N/A'),
                'driver': f"{standing['Driver']['givenName']} {standing['Driver']['familyName']}",
                'constructor': standing['Constructors'][0]['name'],
                'points': standing.get('points', '0'),
                'wins': standing.get('wins', '0')
            })
        
        return formatted_standings
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []

def fetch_constructor_standings(year: int, round_number: Optional[int] = None) -> List[Dict]:
    """
    Fetch constructor championship standings
    """
    if round_number:
        url = f"{BASE_URL}/{year}/{round_number}/constructorStandings.json"
    else:
        url = f"{BASE_URL}/{year}/constructorStandings.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        standings_lists = data.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
        
        if not standings_lists:
            return []
        
        standings = standings_lists[0].get('ConstructorStandings', [])
        
        formatted_standings = []
        for standing in standings:
            formatted_standings.append({
                'position': standing.get('position', 'N/A'),
                'constructor': standing['Constructor']['name'],
                'points': standing.get('points', '0'),
                'wins': standing.get('wins', '0')
            })
        
        return formatted_standings
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []