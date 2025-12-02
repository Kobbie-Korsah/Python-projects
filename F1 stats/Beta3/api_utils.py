"""
F1 Dashboard Beta 3 - Jolpica-F1 API Utilities
Enhanced API functions with caching
"""
import requests
from typing import List, Dict, Optional
from data_cache import get_cache

BASE_URL = "https://api.jolpi.ca/ergast/f1"

def fetch_race_results(year: int, race_name: str) -> List[Dict]:
    """
    Fetch race results with caching
    
    Args:
        year (int): Season year
        race_name (str): Race name
    
    Returns:
        List[Dict]: Race results
    """
    cache = get_cache()
    cache_key = f"race_results_{year}_{race_name}"
    
    # Check cache
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    race_map = {
        "Bahrain": 1, "Saudi Arabia": 2, "Australia": 3, "Japan": 4, "China": 5,
        "Miami": 6, "Emilia Romagna": 7, "Monaco": 8, "Canada": 9, "Spain": 10,
        "Austria": 11, "Great Britain": 12, "Hungary": 13, "Belgium": 14,
        "Netherlands": 15, "Italy": 16, "Azerbaijan": 17, "Singapore": 18,
        "United States": 19, "Mexico": 20, "Brazil": 21, "Las Vegas": 22,
        "Qatar": 23, "Abu Dhabi": 24
    }
    
    round_number = race_map.get(race_name, 1)
    url = f"{BASE_URL}/{year}/{round_number}/results.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
        
        if not races:
            return []
        
        results = races[0].get('Results', [])
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                'position': result.get('position', 'N/A'),
                'driver': f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                'driver_code': result['Driver'].get('code', 'N/A'),
                'constructor': result['Constructor']['name'],
                'points': result.get('points', '0'),
                'status': result.get('status', 'N/A'),
                'grid': result.get('grid', 'N/A'),
                'laps': result.get('laps', 'N/A')
            })
        
        # Cache results
        cache.set(cache_key, formatted_results)
        
        return formatted_results
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []

def fetch_driver_standings(year: int, round_number: Optional[int] = None) -> List[Dict]:
    """
    Fetch driver championship standings with caching
    
    Args:
        year (int): Season year
        round_number (int, optional): Specific round
    
    Returns:
        List[Dict]: Driver standings
    """
    cache = get_cache()
    cache_key = f"driver_standings_{year}_{round_number or 'final'}"
    
    # Check cache
    cached = cache.get(cache_key)
    if cached:
        return cached
    
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
                'driver_code': standing['Driver'].get('code', 'N/A'),
                'constructor': standing['Constructors'][0]['name'],
                'points': standing.get('points', '0'),
                'wins': standing.get('wins', '0')
            })
        
        # Cache standings
        cache.set(cache_key, formatted_standings)
        
        return formatted_standings
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []

def fetch_constructor_standings(year: int, round_number: Optional[int] = None) -> List[Dict]:
    """
    Fetch constructor championship standings
    
    Args:
        year (int): Season year
        round_number (int, optional): Specific round
    
    Returns:
        List[Dict]: Constructor standings
    """
    cache = get_cache()
    cache_key = f"constructor_standings_{year}_{round_number or 'final'}"
    
    cached = cache.get(cache_key)
    if cached:
        return cached
    
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
        
        cache.set(cache_key, formatted_standings)
        
        return formatted_standings
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []

def fetch_qualifying_results(year: int, race_name: str) -> List[Dict]:
    """
    Fetch qualifying results
    
    Args:
        year (int): Season year
        race_name (str): Race name
    
    Returns:
        List[Dict]: Qualifying results
    """
    race_map = {
        "Bahrain": 1, "Saudi Arabia": 2, "Australia": 3, "Japan": 4, "China": 5,
        "Miami": 6, "Emilia Romagna": 7, "Monaco": 8, "Canada": 9, "Spain": 10,
        "Austria": 11, "Great Britain": 12, "Hungary": 13, "Belgium": 14,
        "Netherlands": 15, "Italy": 16, "Azerbaijan": 17, "Singapore": 18,
        "United States": 19, "Mexico": 20, "Brazil": 21, "Las Vegas": 22,
        "Qatar": 23, "Abu Dhabi": 24
    }
    
    round_number = race_map.get(race_name, 1)
    url = f"{BASE_URL}/{year}/{round_number}/qualifying.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
        
        if not races:
            return []
        
        quali_results = races[0].get('QualifyingResults', [])
        
        formatted_results = []
        for result in quali_results:
            formatted_results.append({
                'position': result.get('position', 'N/A'),
                'driver': f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                'constructor': result['Constructor']['name'],
                'q1': result.get('Q1', 'N/A'),
                'q2': result.get('Q2', 'N/A'),
                'q3': result.get('Q3', 'N/A')
            })
        
        return formatted_results
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []

def get_race_schedule(year: int) -> List[Dict]:
    """
    Fetch race schedule for a season
    
    Args:
        year (int): Season year
    
    Returns:
        List[Dict]: Race schedule
    """
    cache = get_cache()
    cache_key = f"race_schedule_{year}"
    
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    url = f"{BASE_URL}/{year}.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
        
        schedule = []
        for race in races:
            schedule.append({
                'round': race.get('round', 'N/A'),
                'name': race.get('raceName', 'N/A'),
                'circuit': race['Circuit']['circuitName'],
                'location': f"{race['Circuit']['Location']['locality']}, {race['Circuit']['Location']['country']}",
                'date': race.get('date', 'N/A'),
                'time': race.get('time', 'N/A')
            })
        
        cache.set(cache_key, schedule)
        
        return schedule
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []

def get_driver_info(driver_id: str) -> Optional[Dict]:
    """
    Get detailed driver information
    
    Args:
        driver_id (str): Driver ID (e.g., 'hamilton')
    
    Returns:
        Dict: Driver information
    """
    url = f"{BASE_URL}/drivers/{driver_id}.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        drivers = data.get('MRData', {}).get('DriverTable', {}).get('Drivers', [])
        
        if not drivers:
            return None
        
        driver = drivers[0]
        return {
            'driver_id': driver.get('driverId'),
            'code': driver.get('code'),
            'number': driver.get('permanentNumber'),
            'name': f"{driver.get('givenName')} {driver.get('familyName')}",
            'dob': driver.get('dateOfBirth'),
            'nationality': driver.get('nationality'),
            'url': driver.get('url')
        }
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None