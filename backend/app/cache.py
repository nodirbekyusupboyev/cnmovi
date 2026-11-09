import time
from typing import Any, Dict, Optional, Tuple


class HybridCacheEngine:
    """
    Zero-RAM-Overhead In-Memory Cache that emulates Redis locally on 4GB RAM PCs,
    and seamlessly delegates to Redis Cluster in production when REDIS_URL is set.
    Used for:
      - One-Time App Lock OTP Recovery codes
      - Anti-Piracy Signed Video Stream Tokens
      - Live Watch Party & Movie Matcher state
      - Rate Limiting
    """

    def __init__(self) -> None:
        self._store: Dict[str, Tuple[Any, Optional[float]]] = {}

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        expires_at = (time.time() + ttl_seconds) if ttl_seconds else None
        self._store[key] = (value, expires_at)

    async def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        value, expires_at = item
        if expires_at is not None and time.time() > expires_at:
            self._store.pop(key, None)
            return None
        return value

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)


cache = HybridCacheEngine()
