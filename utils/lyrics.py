"""
RAXI MUSIC - Lyrics Fetcher
Uses lyrics.ovh (free, no key required)
"""

import aiohttp
from utils.logger import get_logger

logger = get_logger(__name__)


async def fetch_lyrics(title: str, artist: str = "") -> str | None:
    """
    Fetch lyrics from lyrics.ovh API.
    Returns lyrics string or None if not found.
    """
    base_url = "https://api.lyrics.ovh/v1"
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{base_url}/{artist or 'unknown'}/{title}"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("lyrics")
    except Exception as e:
        logger.debug(f"Lyrics fetch failed: {e}")

    # Fallback: search by title only
    try:
        async with aiohttp.ClientSession() as session:
            search_url = f"https://api.lyrics.ovh/suggest/{title}"
            async with session.get(search_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    hits = data.get("data", [])
                    if hits:
                        hit = hits[0]
                        art = hit.get("artist", {}).get("name", "")
                        ttl = hit.get("title", title)
                        url = f"{base_url}/{art}/{ttl}"
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r2:
                            if r2.status == 200:
                                d2 = await r2.json()
                                return d2.get("lyrics")
    except Exception as e:
        logger.debug(f"Lyrics fallback failed: {e}")

    return None
