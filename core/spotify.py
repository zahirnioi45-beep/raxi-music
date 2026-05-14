"""
RAXI MUSIC - Spotify Metadata Fetcher
Fetches track metadata from Spotify, then streams via YouTube
"""

import re
import aiohttp
from typing import Optional
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_TRACK_URL = "https://api.spotify.com/v1/tracks/{track_id}"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

SPOTIFY_TRACK_RE = re.compile(
    r"(?:https?://)?(?:open\.)?spotify\.com/track/([a-zA-Z0-9]+)"
)
SPOTIFY_PLAYLIST_RE = re.compile(
    r"(?:https?://)?(?:open\.)?spotify\.com/playlist/([a-zA-Z0-9]+)"
)


class SpotifyManager:
    def __init__(self):
        self._token: Optional[str] = None
        self._token_expires: int = 0

    def _is_spotify_url(self, url: str) -> bool:
        return "spotify.com" in url

    def _extract_track_id(self, url: str) -> Optional[str]:
        m = SPOTIFY_TRACK_RE.search(url)
        return m.group(1) if m else None

    async def _get_token(self) -> Optional[str]:
        import time
        if self._token and time.time() < self._token_expires:
            return self._token

        if not Config.SPOTIFY_CLIENT_ID or not Config.SPOTIFY_CLIENT_SECRET:
            return None

        try:
            import base64
            creds = f"{Config.SPOTIFY_CLIENT_ID}:{Config.SPOTIFY_CLIENT_SECRET}"
            encoded = base64.b64encode(creds.encode()).decode()
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    SPOTIFY_TOKEN_URL,
                    data={"grant_type": "client_credentials"},
                    headers={"Authorization": f"Basic {encoded}"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self._token = data["access_token"]
                        self._token_expires = int(time.time()) + data["expires_in"] - 60
                        return self._token
        except Exception as e:
            logger.error(f"Spotify token error: {e}")
        return None

    async def get_track_info(self, url: str) -> Optional[dict]:
        """Get Spotify track metadata."""
        track_id = self._extract_track_id(url)
        if not track_id:
            return None

        token = await self._get_token()
        if not token:
            # No credentials — extract from URL pattern
            return {"title": "Spotify Track", "artist": "", "search_query": None}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    SPOTIFY_TRACK_URL.format(track_id=track_id),
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        title = data["name"]
                        artist = ", ".join(a["name"] for a in data["artists"])
                        album = data.get("album", {}).get("name", "")
                        thumb = (data.get("album", {}).get("images") or [{}])[0].get("url", "")
                        duration_ms = data.get("duration_ms", 0)
                        return {
                            "title": title,
                            "artist": artist,
                            "album": album,
                            "thumbnail": thumb,
                            "duration": duration_ms // 1000,
                            "search_query": f"{title} {artist}",
                            "source": "spotify",
                        }
        except Exception as e:
            logger.error(f"Spotify track fetch error: {e}")
        return None

    def is_spotify(self, url: str) -> bool:
        return self._is_spotify_url(url)


spotify = SpotifyManager()
