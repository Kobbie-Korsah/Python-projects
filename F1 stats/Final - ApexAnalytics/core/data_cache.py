"""
F1 Analytics Suite - Data Caching System
Intelligent memory and disk caching with expiry
"""

import pickle
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Dict
from core.enums import CACHE_EXPIRY_HOURS, MAX_CACHE_SIZE_MB

class CacheManager:
    """Manages application-wide data caching"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, cache_dir: str = 'cache', expiry_hours: int = CACHE_EXPIRY_HOURS):
        if self._initialized:
            return
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.expiry_delta = timedelta(hours=expiry_hours)
        self.memory_cache: Dict[str, tuple] = {}
        self.max_memory_items = 50
        self._initialized = True
    
    def get(self, key: str, use_memory: bool = True) -> Optional[Any]:
        """Retrieve data from cache"""
        if use_memory and key in self.memory_cache:
            data, timestamp = self.memory_cache[key]
            if datetime.now() - timestamp < self.expiry_delta:
                return data
            else:
                del self.memory_cache[key]
        
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                data, timestamp = pickle.load(f)
            
            if datetime.now() - timestamp > self.expiry_delta:
                cache_path.unlink()
                return None
            
            self._set_memory_cache(key, data, timestamp)
            return data
        
        except Exception as e:
            print(f"Cache read error for {key}: {e}")
            return None
    
    def set(self, key: str, data: Any, persist: bool = True) -> bool:
        """Store data in cache"""
        timestamp = datetime.now()
        
        self._set_memory_cache(key, data, timestamp)
        
        if persist:
            try:
                cache_path = self._get_cache_path(key)
                with open(cache_path, 'wb') as f:
                    pickle.dump((data, timestamp), f, protocol=pickle.HIGHEST_PROTOCOL)
                return True
            except Exception as e:
                print(f"Cache write error for {key}: {e}")
                return False
        
        return True
    
    def delete(self, key: str) -> bool:
        """Delete cached data"""
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            try:
                cache_path.unlink()
                return True
            except Exception as e:
                print(f"Cache delete error for {key}: {e}")
                return False
        
        return True
    
    def clear_all(self) -> int:
        """Clear all cached data"""
        self.memory_cache.clear()
        
        deleted_count = 0
        for cache_file in self.cache_dir.glob('*.pkl'):
            try:
                cache_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {cache_file}: {e}")
        
        return deleted_count
    
    def get_cache_size(self) -> int:
        """Get total cache size in bytes"""
        total_size = 0
        for cache_file in self.cache_dir.glob('*.pkl'):
            try:
                total_size += cache_file.stat().st_size
            except:
                pass
        return total_size
    
    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key"""
        safe_key = key.replace('/', '_').replace('\\', '_').replace(':', '_')
        return self.cache_dir / f"{safe_key}.pkl"
    
    def _set_memory_cache(self, key: str, data: Any, timestamp: datetime):
        """Store in memory cache with LRU eviction"""
        if len(self.memory_cache) >= self.max_memory_items:
            oldest_key = min(self.memory_cache.items(), key=lambda x: x[1][1])[0]
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = (data, timestamp)

def get_cache() -> CacheManager:
    """Get global cache instance"""
    return CacheManager()