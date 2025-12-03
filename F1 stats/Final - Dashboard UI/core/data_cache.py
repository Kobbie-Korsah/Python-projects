"""
Lightweight in-memory cache with time-based expiry.
Used to avoid repeated FastF1 and Jolpica API calls.
"""

import time
from typing import Any, Dict, Optional, Tuple


class DataCache:
    """Simple dictionary-backed cache with TTL semantics."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Return cached value if it has not expired."""
        entry = self._store.get(key)
        if not entry:
            return None
        timestamp, value = entry
        if time.time() - timestamp > self.ttl_seconds:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        """Store a value with the current timestamp."""
        self._store[key] = (time.time(), value)

    def clear(self) -> None:
        """Drop all cached data."""
        self._store.clear()
