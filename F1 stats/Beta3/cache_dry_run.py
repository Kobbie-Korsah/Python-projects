"""
Lightweight dry-run to validate CacheManager behaviour without network calls.

Run with: `python cache_dry_run.py`
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep

from data_cache import CacheManager


def run_dry_run() -> bool:
    with TemporaryDirectory() as tmp_dir:
        cache_path = Path(tmp_dir)
        cache = CacheManager(cache_dir=cache_path, expiry_hours=0.0003)  # ~1 second

        # Write and read
        cache.set("sample_key", {"value": 42})
        immediate = cache.get("sample_key")
        if immediate != {"value": 42}:
            print("FAIL: Immediate read mismatch", immediate)
            return False

        # Ensure file exists
        files = list(cache_path.glob("*.pkl"))
        if not files:
            print("FAIL: Cache file not written")
            return False

        # Expiry path
        sleep(1.2)  # allow expiry window to elapse
        expired = cache.get("sample_key")
        if expired is not None:
            print("FAIL: Cache entry did not expire as expected", expired)
            return False

        # Clear_all should be safe on empty and non-empty
        cache.set("another_key", {"value": "test"})
        cache.clear_all()
        if cache.get("another_key") is not None:
            print("FAIL: clear_all did not purge entries")
            return False

        print("PASS: CacheManager dry-run succeeded")
        return True


if __name__ == "__main__":
    run_dry_run()
