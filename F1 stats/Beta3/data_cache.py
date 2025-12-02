"""
F1 Dashboard Beta 3 - Data Caching Manager
Cache expensive API and FastF1 calls to improve performance
"""
import pickle
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple, Any, Optional

class CacheManager:
    """Manages caching of session data and API responses"""
    
    def __init__(self, cache_dir='app_cache', expiry_hours=24):
        """
        Initialize cache manager
        
        Args:
            cache_dir (str): Directory to store cache files
            expiry_hours (int): Hours before cache expires
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.expiry_delta = timedelta(hours=expiry_hours)
        self.memory_cache = {}
    
    def _get_cache_path(self, key):
        """Get file path for cache key"""
        safe_key = key.replace('/', '_').replace('\\', '_')
        return self.cache_dir / f"{safe_key}.pkl"
    
    def get(self, key):
        """
        Get cached data
        
        Args:
            key (str): Cache key
        
        Returns:
            object: Cached data or None if not found/expired
        """
        # Check memory cache first
        if key in self.memory_cache:
            data, timestamp = self.memory_cache[key]
            if datetime.now() - timestamp < self.expiry_delta:
                return data
            else:
                del self.memory_cache[key]
        
        # Check file cache
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                data, timestamp = pickle.load(f)
            
            # Check if expired
            if datetime.now() - timestamp > self.expiry_delta:
                cache_path.unlink()
                return None
            
            # Store in memory cache
            self.memory_cache[key] = (data, timestamp)
            return data
        
        except Exception as e:
            print(f"Cache read error for {key}: {e}")
            return None
    
    def set(self, key, data):
        """
        Store data in cache
        
        Args:
            key (str): Cache key
            data (object): Data to cache
        """
        timestamp = datetime.now()
        
        # Store in memory
        self.memory_cache[key] = (data, timestamp)
        
        # Store in file
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump((data, timestamp), f)
        except Exception as e:
            print(f"Cache write error for {key}: {e}")
    
    def delete(self, key):
        """
        Delete cached data
        
        Args:
            key (str): Cache key
        """
        # Remove from memory
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # Remove file
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
    
    def clear_all(self):
        """Clear all cached data"""
        # Clear memory
        self.memory_cache.clear()
        
        # Clear files
        for cache_file in self.cache_dir.glob('*.pkl'):
            try:
                cache_file.unlink()
            except Exception as e:
                print(f"Error deleting {cache_file}: {e}")
    
    def clear_expired(self):
        """Remove expired cache files"""
        now = datetime.now()
        
        for cache_file in self.cache_dir.glob('*.pkl'):
            try:
                with open(cache_file, 'rb') as f:
                    _, timestamp = pickle.load(f)
                
                if now - timestamp > self.expiry_delta:
                    cache_file.unlink()
            except Exception:
                # If we can't read it, delete it
                cache_file.unlink()
    
    def get_cache_size(self):
        """
        Get total size of cache
        
        Returns:
            int: Size in bytes
        """
        total_size = 0
        for cache_file in self.cache_dir.glob('*.pkl'):
            total_size += cache_file.stat().st_size
        return total_size
    
    def get_cache_info(self):
        """
        Get cache statistics
        
        Returns:
            dict: Cache info
        """
        files = list(self.cache_dir.glob('*.pkl'))
        
        return {
            'file_count': len(files),
            'memory_count': len(self.memory_cache),
            'total_size_bytes': self.get_cache_size(),
            'total_size_mb': self.get_cache_size() / (1024 * 1024)
        }

# Global cache instance
_global_cache = None

def get_cache():
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache
