"""
╔══════════════════════════════════════════════╗
║      RAXI MUSIC - Database Models            ║
║      High-level async CRUD wrappers          ║
╚══════════════════════════════════════════════╝
"""

import time
from typing import Optional
from .engine import db


# ─── Chat Model ───────────────────────────────────────────────────────────────

class ChatDB:
    @staticmethod
    async def add(chat_id: int, title: str = ""):
        if not db.exists("chats", str(chat_id)):
            await db.set("chats", str(chat_id), {
                "chat_id": chat_id,
                "title": title,
                "joined": int(time.time()),
                "loop": False,
                "volume": 100,
                "247_mode": False,
            })

    @staticmethod
    async def remove(chat_id: int):
        await db.delete("chats", str(chat_id))

    @staticmethod
    def get(chat_id: int) -> dict:
        return db.get("chats", str(chat_id), {})

    @staticmethod
    def all() -> dict:
        return db.get_all("chats")

    @staticmethod
    def count() -> int:
        return len(db.get_all("chats"))

    @staticmethod
    async def set_loop(chat_id: int, mode: str):
        """mode: 'off', 'one', 'all'"""
        await db.update("chats", str(chat_id), {"loop": mode})

    @staticmethod
    def get_loop(chat_id: int) -> str:
        return db.get("chats", str(chat_id), {}).get("loop", "off")

    @staticmethod
    async def set_volume(chat_id: int, vol: int):
        await db.update("chats", str(chat_id), {"volume": vol})

    @staticmethod
    def get_volume(chat_id: int) -> int:
        return db.get("chats", str(chat_id), {}).get("volume", 100)

    @staticmethod
    async def set_247(chat_id: int, state: bool):
        await db.update("chats", str(chat_id), {"247_mode": state})

    @staticmethod
    def get_247(chat_id: int) -> bool:
        return db.get("chats", str(chat_id), {}).get("247_mode", False)


# ─── User Model ───────────────────────────────────────────────────────────────

class UserDB:
    @staticmethod
    async def add(user_id: int, name: str = "", username: str = ""):
        if not db.exists("users", str(user_id)):
            await db.set("users", str(user_id), {
                "user_id": user_id,
                "name": name,
                "username": username,
                "joined": int(time.time()),
                "songs_played": 0,
            })

    @staticmethod
    def get(user_id: int) -> dict:
        return db.get("users", str(user_id), {})

    @staticmethod
    def all() -> dict:
        return db.get_all("users")

    @staticmethod
    def count() -> int:
        return len(db.get_all("users"))

    @staticmethod
    async def increment_songs(user_id: int):
        await db.increment("users", str(user_id), "songs_played")


# ─── Queue Model ──────────────────────────────────────────────────────────────

class QueueDB:
    @staticmethod
    def get(chat_id: int) -> list:
        return db.get("queue", str(chat_id), [])

    @staticmethod
    async def set(chat_id: int, queue: list):
        await db.set("queue", str(chat_id), queue)

    @staticmethod
    async def add_track(chat_id: int, track: dict):
        q = QueueDB.get(chat_id)
        q.append(track)
        await db.set("queue", str(chat_id), q)

    @staticmethod
    async def remove_first(chat_id: int) -> Optional[dict]:
        q = QueueDB.get(chat_id)
        if not q:
            return None
        track = q.pop(0)
        await db.set("queue", str(chat_id), q)
        return track

    @staticmethod
    async def clear(chat_id: int):
        await db.set("queue", str(chat_id), [])

    @staticmethod
    def length(chat_id: int) -> int:
        return len(QueueDB.get(chat_id))


# ─── Sudo Model ───────────────────────────────────────────────────────────────

class SudoDB:
    @staticmethod
    def get_all() -> list[int]:
        data = db.get("sudo", "users", [])
        return [int(x) for x in data]

    @staticmethod
    async def add(user_id: int):
        users = SudoDB.get_all()
        if user_id not in users:
            users.append(user_id)
            await db.set("sudo", "users", users)

    @staticmethod
    async def remove(user_id: int):
        users = SudoDB.get_all()
        if user_id in users:
            users.remove(user_id)
            await db.set("sudo", "users", users)

    @staticmethod
    def is_sudo(user_id: int) -> bool:
        return user_id in SudoDB.get_all()


# ─── Stats Model ──────────────────────────────────────────────────────────────

class StatsDB:
    @staticmethod
    async def increment(field: str, by: int = 1):
        await db.increment("stats", "global", field, by)

    @staticmethod
    def get() -> dict:
        return db.get("stats", "global", {
            "songs_played": 0,
            "commands_used": 0,
            "errors": 0,
            "start_time": int(time.time()),
        })

    @staticmethod
    async def set_start_time():
        stats = StatsDB.get()
        if "start_time" not in stats:
            await db.update("stats", "global", {"start_time": int(time.time())})


# ─── Settings Model ───────────────────────────────────────────────────────────

class SettingsDB:
    @staticmethod
    async def set_maintenance(state: bool):
        await db.update("settings", "global", {"maintenance": state})

    @staticmethod
    def is_maintenance() -> bool:
        return db.get("settings", "global", {}).get("maintenance", False)

    @staticmethod
    async def set(key: str, value):
        await db.update("settings", "global", {key: value})

    @staticmethod
    def get(key: str, default=None):
        return db.get("settings", "global", {}).get(key, default)
