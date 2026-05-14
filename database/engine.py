"""
╔══════════════════════════════════════════════╗
║      RAXI MUSIC - JSON Database Engine       ║
║   Async · Safe Write · Anti-Corrupt · Cache  ║
╚══════════════════════════════════════════════╝
"""

import asyncio
import json
import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")


class JsonDB:
    """
    Async JSON database engine with:
    - In-memory cache
    - Safe atomic writes (temp file → rename)
    - Auto-save on change
    - Anti-corruption: write to .tmp then rename
    """

    def __init__(self):
        self._cache: dict[str, dict] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._dirty: dict[str, bool] = {}
        self._files = {
            "chats": os.path.join(DB_DIR, "chats.json"),
            "users": os.path.join(DB_DIR, "users.json"),
            "queue": os.path.join(DB_DIR, "queue.json"),
            "sudo": os.path.join(DB_DIR, "sudo.json"),
            "stats": os.path.join(DB_DIR, "stats.json"),
            "settings": os.path.join(DB_DIR, "settings.json"),
        }

    def _get_lock(self, name: str) -> asyncio.Lock:
        if name not in self._locks:
            self._locks[name] = asyncio.Lock()
        return self._locks[name]

    async def load_all(self):
        """Load all JSON files into memory on startup."""
        os.makedirs(DB_DIR, exist_ok=True)
        for name, path in self._files.items():
            await self._load(name, path)
        logger.info("✅ Database loaded — all JSON files in memory")

    async def _load(self, name: str, path: str):
        lock = self._get_lock(name)
        async with lock:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self._cache[name] = json.load(f)
                except (json.JSONDecodeError, OSError) as e:
                    logger.warning(f"⚠️ Corrupt {path}: {e} — resetting to {{}}")
                    self._cache[name] = {}
            else:
                self._cache[name] = {}
                await self._save(name)

    async def _save(self, name: str):
        """Atomic write: write to .tmp then rename."""
        path = self._files[name]
        tmp_path = path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self._cache[name], f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, path)
        except OSError as e:
            logger.error(f"❌ Failed to save {name}: {e}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def get(self, collection: str, key: str, default: Any = None) -> Any:
        """Sync get from cache."""
        return self._cache.get(collection, {}).get(key, default)

    def get_all(self, collection: str) -> dict:
        """Get entire collection from cache."""
        return self._cache.get(collection, {})

    async def set(self, collection: str, key: str, value: Any):
        """Set value and save."""
        lock = self._get_lock(collection)
        async with lock:
            if collection not in self._cache:
                self._cache[collection] = {}
            self._cache[collection][key] = value
            await self._save(collection)

    async def delete(self, collection: str, key: str):
        """Delete key and save."""
        lock = self._get_lock(collection)
        async with lock:
            self._cache.get(collection, {}).pop(key, None)
            await self._save(collection)

    async def update(self, collection: str, key: str, data: dict):
        """Merge dict into existing entry."""
        lock = self._get_lock(collection)
        async with lock:
            if collection not in self._cache:
                self._cache[collection] = {}
            existing = self._cache[collection].get(key, {})
            if isinstance(existing, dict):
                existing.update(data)
                self._cache[collection][key] = existing
            else:
                self._cache[collection][key] = data
            await self._save(collection)

    def exists(self, collection: str, key: str) -> bool:
        return key in self._cache.get(collection, {})

    async def increment(self, collection: str, key: str, field: str, by: int = 1):
        """Increment numeric field."""
        lock = self._get_lock(collection)
        async with lock:
            if collection not in self._cache:
                self._cache[collection] = {}
            entry = self._cache[collection].get(key, {})
            entry[field] = entry.get(field, 0) + by
            self._cache[collection][key] = entry
            await self._save(collection)


# Global DB instance
db = JsonDB()
