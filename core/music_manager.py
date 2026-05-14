"""
╔══════════════════════════════════════════════╗
║      RAXI MUSIC - Core Music Manager         ║
║  PyTgCalls · Queue · Loop · Shuffle · Voice  ║
╚══════════════════════════════════════════════╝
"""

import asyncio
import random
import time
from typing import Optional, TYPE_CHECKING

from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

from database import QueueDB, ChatDB, StatsDB
from core.ytdl import ytdl
from utils.logger import get_logger
from utils.helpers import format_duration, truncate

if TYPE_CHECKING:
    from pyrogram import Client

logger = get_logger(__name__)


class ActiveStream:
    __slots__ = ("track", "started_at", "paused", "chat_id")

    def __init__(self, track: dict, chat_id: int):
        self.track = track
        self.started_at = time.time()
        self.paused = False
        self.chat_id = chat_id

    def elapsed(self) -> int:
        if self.paused:
            return 0
        return int(time.time() - self.started_at)


class MusicManager:
    def __init__(self):
        self._active: dict[int, ActiveStream] = {}
        self._call: Optional["PyTgCalls"] = None
        self._bot: Optional["Client"] = None

    def set_clients(self, bot: "Client", call: "PyTgCalls"):
        self._bot = bot
        self._call = call

    async def play(self, chat_id: int, track: dict) -> bool:
        if not self._call:
            logger.error("PyTgCalls not initialised")
            return False

        stream_url = track.get("url")
        if not stream_url:
            logger.error(f"No stream URL for: {track.get('title')}")
            return False

        try:
            audio = AudioPiped(stream_url)
            try:
                await self._call.change_stream(chat_id, audio)
                logger.info(f"🔄 Changed stream in {chat_id}: {track['title']}")
            except Exception:
                await self._call.join_group_call(chat_id, audio)
                logger.info(f"✅ Joined voice chat in {chat_id}: {track['title']}")

            self._active[chat_id] = ActiveStream(track, chat_id)
            await StatsDB.increment("songs_played")
            return True

        except Exception as e:
            logger.error(f"Play error in {chat_id}: {e}")
            return False

    async def queue_and_play(self, chat_id: int, track: dict, force: bool = False) -> dict:
        if force or chat_id not in self._active:
            ok = await self.play(chat_id, track)
            if ok:
                await QueueDB.clear(chat_id)
                return {"status": "playing", "track": track}
            return {"status": "error", "track": track}
        else:
            await QueueDB.add_track(chat_id, track)
            pos = QueueDB.length(chat_id)
            return {"status": "queued", "position": pos, "track": track}

    async def skip(self, chat_id: int) -> Optional[dict]:
        loop_mode = ChatDB.get_loop(chat_id)

        if loop_mode == "one" and chat_id in self._active:
            track = self._active[chat_id].track
            await self.play(chat_id, track)
            return track

        next_track = await QueueDB.remove_first(chat_id)
        if next_track:
            if loop_mode == "all" and chat_id in self._active:
                await QueueDB.add_track(chat_id, self._active[chat_id].track)
            await self.play(chat_id, next_track)
            return next_track
        else:
            await self.stop(chat_id)
            return None

    async def stop(self, chat_id: int):
        try:
            if self._call:
                await self._call.leave_group_call(chat_id)
        except Exception as e:
            logger.debug(f"Stop error in {chat_id}: {e}")
        finally:
            self._active.pop(chat_id, None)
            await QueueDB.clear(chat_id)

    async def pause(self, chat_id: int) -> bool:
        try:
            if self._call and chat_id in self._active:
                await self._call.pause_stream(chat_id)
                self._active[chat_id].paused = True
                return True
        except Exception as e:
            logger.error(f"Pause error: {e}")
        return False

    async def resume(self, chat_id: int) -> bool:
        try:
            if self._call and chat_id in self._active:
                await self._call.resume_stream(chat_id)
                self._active[chat_id].paused = False
                return True
        except Exception as e:
            logger.error(f"Resume error: {e}")
        return False

    async def set_volume(self, chat_id: int, volume: int) -> bool:
        volume = max(1, min(200, volume))
        try:
            if self._call:
                await self._call.change_volume_call(chat_id, volume)
                await ChatDB.set_volume(chat_id, volume)
                return True
        except Exception as e:
            logger.error(f"Volume error: {e}")
        return False

    async def shuffle_queue(self, chat_id: int) -> bool:
        q = QueueDB.get(chat_id)
        if len(q) < 2:
            return False
        random.shuffle(q)
        await QueueDB.set(chat_id, q)
        return True

    async def on_stream_end(self, chat_id: int):
        loop_mode = ChatDB.get_loop(chat_id)

        if loop_mode == "one" and chat_id in self._active:
            track = self._active[chat_id].track
            refreshed = await ytdl.search(track.get("video_url", track.get("title", "")))
            if refreshed:
                track["url"] = refreshed["url"]
            await self.play(chat_id, track)
            return

        if loop_mode == "all" and chat_id in self._active:
            current = self._active[chat_id].track
            await QueueDB.add_track(chat_id, current)

        next_track = await QueueDB.remove_first(chat_id)
        if next_track:
            refreshed = await ytdl.search(next_track.get("video_url", next_track.get("title", "")))
            if refreshed:
                next_track["url"] = refreshed["url"]
            ok = await self.play(chat_id, next_track)
            if ok and self._bot:
                try:
                    await self._bot.send_message(
                        chat_id,
                        self._now_playing_text(next_track),
                        parse_mode="markdown",
                    )
                except Exception:
                    pass
        else:
            self._active.pop(chat_id, None)
            if not ChatDB.get_247(chat_id):
                try:
                    if self._call:
                        await self._call.leave_group_call(chat_id)
                except Exception:
                    pass

    def _now_playing_text(self, track: dict) -> str:
        title = truncate(track.get("title", "Unknown"), 40)
        duration = format_duration(track.get("duration", 0))
        return (
            f"🎵 **Now Playing**\n"
            f"┏ **{title}**\n"
            f"┣ 🕐 `{duration}`\n"
            f"┗ 📡 `{track.get('source', 'youtube').upper()}`"
        )

    def is_playing(self, chat_id: int) -> bool:
        return chat_id in self._active and not self._active[chat_id].paused

    def is_paused(self, chat_id: int) -> bool:
        return chat_id in self._active and self._active[chat_id].paused

    def is_active(self, chat_id: int) -> bool:
        return chat_id in self._active

    def current_track(self, chat_id: int) -> Optional[dict]:
        s = self._active.get(chat_id)
        return s.track if s else None

    def elapsed(self, chat_id: int) -> int:
        s = self._active.get(chat_id)
        return s.elapsed() if s else 0


music = MusicManager()
