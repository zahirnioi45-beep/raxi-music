"""
╔══════════════════════════════════════════════╗
║         RAXI MUSIC - Configuration           ║
║         Dark Anime Aesthetic Modern          ║
╚══════════════════════════════════════════════╝
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Telegram API ─────────────────────────────
    API_ID: int = int(os.getenv("API_ID", 0))
    API_HASH: str = os.getenv("API_HASH", "")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    STRING_SESSION: str = os.getenv("STRING_SESSION", "")

    # ── Owner ─────────────────────────────────────
    OWNER_ID: int = int(os.getenv("OWNER_ID", 0))
    OWNER_USERNAME: str = os.getenv("OWNER_USERNAME", "owner")
    SUDO_USERS: list[int] = [
        int(x)
        for x in os.getenv("SUDO_USERS", "").split(",")
        if x.strip().isdigit()
    ]

    # ── Bot Info ──────────────────────────────────
    BOT_NAME: str = os.getenv("BOT_NAME", "RAXI MUSIC")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "raximusic_bot")

    # ── Spotify ───────────────────────────────────
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")

    # ── Donate ────────────────────────────────────
    DONATE_LINK: str = os.getenv("DONATE_LINK", "https://saweria.co/raxi")
    QRIS_LINK: str = os.getenv("QRIS_LINK", "")
    TRAKTEER_LINK: str = os.getenv("TRAKTEER_LINK", "")

    # ── Performance ───────────────────────────────
    MAX_QUEUE_SIZE: int = int(os.getenv("MAX_QUEUE_SIZE", 50))
    DOWNLOAD_TIMEOUT: int = int(os.getenv("DOWNLOAD_TIMEOUT", 60))
    CACHE_CLEANUP_INTERVAL: int = int(os.getenv("CACHE_CLEANUP_INTERVAL", 3600))

    # ── Paths ─────────────────────────────────────
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_DIR: str = os.path.join(BASE_DIR, "database")
    CACHE_DIR: str = os.path.join(BASE_DIR, "cache")
    DOWNLOAD_DIR: str = os.path.join(BASE_DIR, "downloads")

    # ── Logging ───────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_CHANNEL: int = int(os.getenv("LOG_CHANNEL", 0))

    # ── Audio Settings ────────────────────────────
    AUDIO_QUALITY: int = 128  # kbps
    DEFAULT_VOLUME: int = 100

    # ── Invite Link (set after bot starts) ────────
    BOT_INVITE_LINK: str = ""
