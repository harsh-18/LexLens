import time
import hashlib
from typing import Any, Optional, Dict, Tuple
from collections import OrderedDict
import threading

class LRUTTLCache:
    """
    High-performance, thread-safe in-memory LRU cache with Time-To-Live (TTL) expiration.
    Used for vector embeddings, repeated document queries, and retrieval results.
    """
    def __init__(self, maxsize: int = 2000, default_ttl: int = 3600):
        self.maxsize = maxsize
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._lock = threading.Lock()
        
        # Telemetry metrics
        self.hits = 0
        self.misses = 0

    def _hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        hashed = self._hash_key(key)
        now = time.time()
        with self._lock:
            if hashed in self._cache:
                val, expires_at = self._cache[hashed]
                if now < expires_at:
                    self._cache.move_to_end(hashed)
                    self.hits += 1
                    return val
                else:
                    del self._cache[hashed]
            self.misses += 1
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        hashed = self._hash_key(key)
        duration = ttl if ttl is not None else self.default_ttl
        expires_at = time.time() + duration
        with self._lock:
            if hashed in self._cache:
                self._cache.move_to_end(hashed)
            self._cache[hashed] = (value, expires_at)
            if len(self._cache) > self.maxsize:
                self._cache.popitem(last=False)

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self.hits + self.misses
            hit_ratio = round((self.hits / total) * 100, 2) if total > 0 else 100.0
            return {
                "size": len(self._cache),
                "maxsize": self.maxsize,
                "hits": self.hits,
                "misses": self.misses,
                "hit_ratio_percent": hit_ratio
            }

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self.hits = 0
            self.misses = 0

# Global singletons
embedding_cache = LRUTTLCache(maxsize=5000, default_ttl=7200)
query_cache = LRUTTLCache(maxsize=1000, default_ttl=1800)
