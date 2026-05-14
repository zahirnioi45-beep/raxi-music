"""
RAXI MUSIC - Global Error Handler
"""

import traceback
from pyrogram import Client
from pyrogram.types import Message
from database import StatsDB
from utils.logger import get_logger

logger = get_logger(__name__)


def setup(app: Client):
    # Pyrogram doesn't have a single global error hook like discord.py,
    # but we can wrap via middleware pattern or handle per plugin.
    # This module provides a shared error logging utility.
    pass


async def handle_error(client: Client, message: Message, error: Exception):
    """Call this in try/except blocks to log and notify."""
    tb = traceback.format_exc()
    logger.error(f"Error in chat {message.chat.id}: {error}\n{tb}")
    await StatsDB.increment("errors")
    try:
        await message.reply_text(
            f"❌ **Terjadi kesalahan:**\n`{str(error)[:200]}`",
            quote=True,
        )
    except Exception:
        pass
