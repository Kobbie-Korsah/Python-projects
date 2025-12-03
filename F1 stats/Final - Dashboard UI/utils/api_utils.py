"""
Wrapper utilities for interacting with the Jolpica F1 API.
All network calls are designed to be run inside Worker threads.
"""

from typing import Any, Dict, Optional

import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"  # Placeholder endpoint; replace with official Jolpica root.


def _headers(api_key: Optional[str]) -> Dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"} if api_key else {}


def fetch_driver_profile(driver_id: str, api_key: Optional[str]) -> Dict[str, Any]:
    """Fetch driver profile data; returns empty dict on failure."""
    url = f"{BASE_URL}/drivers/{driver_id}"
    try:
        resp = requests.get(url, headers=_headers(api_key), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}


def fetch_driver_stats(driver_id: str, api_key: Optional[str]) -> Dict[str, Any]:
    url = f"{BASE_URL}/drivers/{driver_id}/stats"
    try:
        resp = requests.get(url, headers=_headers(api_key), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}


def fetch_constructor(constructor_id: str, api_key: Optional[str]) -> Dict[str, Any]:
    url = f"{BASE_URL}/constructors/{constructor_id}"
    try:
        resp = requests.get(url, headers=_headers(api_key), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}


def fetch_constructor_standings(constructor_id: str, api_key: Optional[str]) -> Dict[str, Any]:
    url = f"{BASE_URL}/constructors/{constructor_id}/standings"
    try:
        resp = requests.get(url, headers=_headers(api_key), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}


def fetch_race_results(season: int, round_no: int, api_key: Optional[str]) -> Dict[str, Any]:
    url = f"{BASE_URL}/race/{season}/{round_no}/results"
    try:
        resp = requests.get(url, headers=_headers(api_key), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}


def fetch_pitstops(season: int, round_no: int, api_key: Optional[str]) -> Dict[str, Any]:
    url = f"{BASE_URL}/race/{season}/{round_no}/pitstops"
    try:
        resp = requests.get(url, headers=_headers(api_key), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}


def fetch_driver_career(driver_id: str, api_key: Optional[str]) -> Dict[str, Any]:
    url = f"{BASE_URL}/driver/{driver_id}/career"
    try:
        resp = requests.get(url, headers=_headers(api_key), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}
