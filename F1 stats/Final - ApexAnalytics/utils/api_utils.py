"""
F1 Analytics Suite - Jolpica F1 API Utilities
Complete API integration with caching and photo path support
"""

import requests
from typing import List, Dict, Optional
from core.data_cache import get_cache
from core.enums import JOLPICA_BASE_URL

def fetch_driver_profile(driver_id: str) -> Dict:
    """Fetch driver profile information"""
    cache = get_cache()
    cache_key = f"driver_profile_{driver_id}"
    
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    url = f"{JOLPICA_BASE_URL}/drivers/{driver_id}.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        drivers = data.get('MRData', {}).get('DriverTable', {}).get('Drivers', [])
        
        if not drivers:
            return {}
        
        driver = drivers[0]
        profile = {
            'driver_id': driver.get('driverId'),
            'code': driver.get('code'),
            'number': driver.get('permanentNumber'),
            'name': f"{driver.get('givenName')} {driver.get('familyName')}",
            'given_name': driver.get('givenName'),
            'family_name': driver.get('familyName'),
            'dob': driver.get('dateOfBirth'),
            'nationality': driver.get('nationality'),
            'url': driver.get('url'),
            # Debut will be filled from standings if available
            'debut': None
        }
        
        cache.set(cache_key, profile)
        return profile
    
    except Exception as e:
        print(f"Error fetching driver profile: {e}")
        return {}

def fetch_driver_career_stats(driver_id: str) -> Dict:
    """Fetch driver career statistics"""
    cache = get_cache()
    cache_key = f"driver_career_{driver_id}"
    
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    url = f"{JOLPICA_BASE_URL}/drivers/{driver_id}/driverStandings.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        standings_lists = data.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
        
        total_wins = 0
        total_points = 0
        championships = 0
        
        for season_list in standings_lists:
            driver_standings = season_list.get('DriverStandings', [])
            if driver_standings:
                standing = driver_standings[0]
                total_wins += int(standing.get('wins', 0))
                total_points += float(standing.get('points', 0))
                if standing.get('position') == '1':
                    championships += 1
        
        # Fetch results for additional stats
        results_url = f"{JOLPICA_BASE_URL}/drivers/{driver_id}/results.json?limit=1000"
        results_response = requests.get(results_url, timeout=10)
        results_data = results_response.json()
        
        races = results_data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
        
        podiums = 0
        poles = 0
        fastest_laps = 0
        dnfs = 0
        total_races = 0
        
        for race in races:
            results = race.get('Results', [])
            if results:
                result = results[0]
                position = result.get('position')
                
                total_races += 1
                
                if position and int(position) <= 3:
                    podiums += 1
                
                if result.get('grid') == '1':
                    poles += 1
                
                if result.get('FastestLap', {}).get('rank') == '1':
                    fastest_laps += 1
                
                status = result.get('status', '')
                if any(word in status for word in ['Accident', 'Collision', 'Engine', 'Gearbox']):
                    dnfs += 1
        
        stats = {
            'championships': championships,
            'wins': total_wins,
            'podiums': podiums,
            'poles': poles,
            'fastest_laps': fastest_laps,
            'points': total_points,
            'dnfs': dnfs,
            'races': total_races,
            'seasons': len(standings_lists),
            'debut': standings_lists[0].get('season') if standings_lists else None
        }
        
        cache.set(cache_key, stats)
        return stats
    
    except Exception as e:
        print(f"Error fetching career stats: {e}")
        return {}

def fetch_driver_season_results(driver_id: str, year: int) -> List[Dict]:
    """Fetch driver results for a specific season"""
    url = f"{JOLPICA_BASE_URL}/{year}/drivers/{driver_id}/results.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
        
        results = []
        for race in races:
            race_results = race.get('Results', [])
            if race_results:
                result = race_results[0]
                results.append({
                    'race': race.get('raceName'),
                    'round': race.get('round'),
                    'date': race.get('date'),
                    'grid': result.get('grid'),
                    'position': result.get('position'),
                    'points': result.get('points'),
                    'status': result.get('status'),
                    'fastest_lap': result.get('FastestLap', {}).get('rank'),
                    'time': result.get('Time', {}).get('time', 'N/A')
                })
        
        return results
    
    except Exception as e:
        print(f"Error fetching season results: {e}")
        return []

def fetch_driver_standings(year: int) -> List[Dict]:
    """Fetch full driver standings for a season."""
    cache = get_cache()
    cache_key = f"driver_standings_{year}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    url = f"{JOLPICA_BASE_URL}/{year}/driverStandings.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        standings_lists = data.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
        if not standings_lists:
            return []

        standings = standings_lists[0].get('DriverStandings', [])
        formatted = []
        for standing in standings:
            driver = standing.get('Driver', {})
            formatted.append({
                'position': int(standing.get('position', 0)),
                'points': float(standing.get('points', 0)),
                'wins': int(standing.get('wins', 0)),
                'driver_id': driver.get('driverId'),
                'code': driver.get('code') or "",
                'number': driver.get('permanentNumber'),
                'name': f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip(),
                'nationality': driver.get('nationality')
            })

        cache.set(cache_key, formatted)
        return formatted
    except Exception as e:
        print(f"Error fetching driver standings: {e}")
        return []

def fetch_constructor_profile(constructor_id: str) -> Dict:
    """Fetch constructor/team profile"""
    cache = get_cache()
    cache_key = f"constructor_profile_{constructor_id}"
    
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    url = f"{JOLPICA_BASE_URL}/constructors/{constructor_id}.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        constructors = data.get('MRData', {}).get('ConstructorTable', {}).get('Constructors', [])
        
        if not constructors:
            return {}
        
        constructor = constructors[0]
        profile = {
            'constructor_id': constructor.get('constructorId'),
            'name': constructor.get('name'),
            'nationality': constructor.get('nationality'),
            'url': constructor.get('url')
        }
        
        cache.set(cache_key, profile)
        return profile
    
    except Exception as e:
        print(f"Error fetching constructor profile: {e}")
        return {}

def fetch_constructor_standings(year: int, constructor_id: Optional[str] = None) -> List[Dict]:
    """Fetch constructor standings"""
    if constructor_id:
        url = f"{JOLPICA_BASE_URL}/{year}/constructors/{constructor_id}/constructorStandings.json"
    else:
        url = f"{JOLPICA_BASE_URL}/{year}/constructorStandings.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        standings_lists = data.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
        
        if not standings_lists:
            return []
        
        standings = standings_lists[0].get('ConstructorStandings', [])
        
        formatted = []
        for standing in standings:
            formatted.append({
                'position': standing.get('position'),
                'constructor': standing['Constructor']['name'],
                'constructor_id': standing['Constructor']['constructorId'],
                'points': standing.get('points'),
                'wins': standing.get('wins')
            })
        
        return formatted
    
    except Exception as e:
        print(f"Error fetching constructor standings: {e}")
        return []


def fetch_constructor_results(year: int, constructor_id: str) -> List[Dict]:
    """Fetch all race results for a constructor in a season."""
    url = f"{JOLPICA_BASE_URL}/{year}/constructors/{constructor_id}/results.json?limit=1000"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
        results = []
        for race in races:
            round_num = race.get('round')
            race_name = race.get('raceName')
            race_results = race.get('Results', [])
            if not race_results:
                continue
            # Sum constructor points (all team drivers) for this race
            race_points = 0.0
            race_podiums = 0
            race_wins = 0
            for result in race_results:
                pts = result.get('points')
                if pts is not None:
                    race_points += float(pts)
                position = result.get('position')
                if position and int(position) == 1:
                    race_wins += 1
                if position and int(position) <= 3:
                    race_podiums += 1
            results.append({
                'round': int(round_num) if round_num else None,
                'race': race_name,
                'points': race_points,
                'wins': race_wins,
                'podiums': race_podiums
            })
        return results
    except Exception as e:
        print(f"Error fetching constructor results: {e}")
        return []

def fetch_race_results(year: int, race: str) -> List[Dict]:
    """Fetch race results"""
    # Map race names to round numbers
    race_map = {
        "Bahrain": 1, "Saudi Arabia": 2, "Australia": 3, "Japan": 4,
        "China": 5, "Miami": 6, "Emilia Romagna": 7, "Monaco": 8,
        "Canada": 9, "Spain": 10, "Austria": 11, "Great Britain": 12,
        "Hungary": 13, "Belgium": 14, "Netherlands": 15, "Italy": 16,
        "Azerbaijan": 17, "Singapore": 18, "United States": 19,
        "Mexico": 20, "Brazil": 21, "Las Vegas": 22, "Qatar": 23,
        "Abu Dhabi": 24
    }
    
    round_num = race_map.get(race, 1)
    url = f"{JOLPICA_BASE_URL}/{year}/{round_num}/results.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
        
        if not races:
            return []
        
        race_data = races[0]
        results = race_data.get('Results', [])
        
        formatted = []
        for result in results:
            formatted.append({
                'position': result.get('position'),
                'driver': f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                'driver_code': result['Driver'].get('code'),
                'constructor': result['Constructor']['name'],
                'grid': result.get('grid'),
                'points': result.get('points'),
                'status': result.get('status')
            })
        
        return formatted
    
    except Exception as e:
        print(f"Error fetching race results: {e}")
        return []

def get_driver_photo_path(driver_code: str) -> str:
    """Get local path to driver photo"""
    return f"assets/logos/drivers/{driver_code}.png"

def get_team_logo_path(team_name: str) -> str:
    """Get local path to team logo"""
    safe_name = team_name.lower().replace(' ', '_')
    return f"assets/logos/teams/{safe_name}.png"
