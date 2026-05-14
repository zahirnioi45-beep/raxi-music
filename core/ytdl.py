"""
╔══════════════════════════════════════════════╗
║       RAXI MUSIC - yt-dlp Manager            ║
║       Audio-only · Fast · Low RAM            ║
╚══════════════════════════════════════════════╝
"""

import asyncio
import os
import re
import time
from typing import Optional
import yt_dlp
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

YOUTUBE_SEARCH_URL = "ytsearch"
AUDIO_FORMAT = "bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio"


def _yt_opts(output_path: str = None) -> dict:
    opts = {
        "format": AUDIO_FORMAT,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "extract_flat": False,
        "geo_bypass": True,
        "socket_timeout": Config.DOWNLOAD_TIMEOUT,
        "retries": 3,
        "postprocessors": [],
    }
    if output_path:
        opts["outtmpl"] = output_path
    return opts


def _search_opts() -> dict:
    return {
        "format": AUDIO_FORMAT,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "extract_flat": "in_playlist",
        "default_search": "ytsearch1",
        "socket_timeout": 15,
    }


class YTDLManager:
    """Handles YouTube search, metadata extraction, and audio download."""

    def __init__(self):
        os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)

    async def search(self, query: str) -> Optional[dict]:
        """Search YouTube and return first result metadata."""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._do_search, query
            )
            return result
        except Exception as e:
            logger.error(f"YT search error: {e}")
            return None

    def _do_search(self, query: str) -> Optional[dict]:
        is_url = query.startswith(("http://", "https://", "www."))
        search_query = query if is_url else f"ytsearch1:{query}"
        try:
            with yt_dlp.YoutubeDL(_search_opts()) as ydl:
                info = ydl.extract_info(search_query, download=False)
                if not info:
                    return None
                # Handle playlist/search results
                if "entries" in info:
                    entries = list(info["entries"])
                    if not entries:
                        return None
                    info = entries[0]
                    # Re-extract full info if it's a flat entry
                    if info.get("_type") == "url" or not info.get("url"):
                        with yt_dlp.YoutubeDL(_yt_opts()) as ydl2:
                            info = ydl2.extract_info(info["url"], download=False)
                return self._parse_info(info)
        except Exception as e:
            logger.error(f"_do_search error: {e}")
            return None

    def _parse_info(self, info: dict) -> dict:
        formats = info.get("formats", [])
        # Pick best audio-only format
        audio_url = None
        for f in reversed(formats):
            if f.get("acodec") != "none" and f.get("vcodec") == "none":
                audio_url = f.get("url")
                break
        if not audio_url:
            audio_url = info.get("url", "")

        return {
            "title": info.get("title", "Unknown"),
            "url": audio_url,
            "video_url": f"https://youtu.be/{info.get('id', '')}",
            "duration": info.get("duration", 0),
            "thumbnail": info.get("thumbnail", ""),
            "channel": info.get("uploader", "Unknown"),
            "views": info.get("view_count", 0),
            "video_id": info.get("id", ""),
            "source": "youtube",
        }

    async def get_stream_url(self, url: str) -> Optional[str]:
        """Get direct streaming URL for an already-known video URL."""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._fetch_stream_url, url)
        except Exception as e:
            logger.error(f"Stream URL error: {e}")
            return None

    def _fetch_stream_url(self, url: str) -> Optional[str]:
        with yt_dlp.YoutubeDL(_yt_opts()) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None
            parsed = self._parse_info(info)
            return parsed.get("url")


ytdl = YTDLManager()
