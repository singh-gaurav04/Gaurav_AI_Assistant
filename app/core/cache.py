import asyncio
from datetime import datetime, timedelta
from typing import Any

_lock = asyncio.Lock()
_store: dict[str, dict[str, Any]] = {}


async def get_cached(key: str) -> Any | None:
    now = datetime.utcnow()
    async with _lock:
        entry = _store.get(key)
        if entry and entry["expires"] > now:
            return entry["value"]
    return None


async def set_cached(key: str, value: Any, ttl_seconds: int = 60) -> None:
    async with _lock:
        _store[key] = {
            "value": value,
            "expires": datetime.utcnow() + timedelta(seconds=ttl_seconds),
        }


async def invalidate_cached(key: str) -> None:
    async with _lock:
        _store.pop(key, None)
