"""
╔════════════════════════════════════════════════════╗
║                                                    ║
║   ██████╗  █████╗ ██╗  ██╗██╗                     ║
║   ██╔══██╗██╔══██╗╚██╗██╔╝██║                     ║
║   ██████╔╝███████║ ╚███╔╝ ██║                     ║
║   ██╔══██╗██╔══██║ ██╔██╗ ██║                     ║
║   ██║  ██║██║  ██║██╔╝ ██╗██║                     ║
║   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝                    ║
║                                                    ║
║   ███╗   ███╗██╗   ██╗███████╗██╗ ██████╗         ║
║   ████╗ ████║██║   ██║██╔════╝██║██╔════╝         ║
║   ██╔████╔██║██║   ██║███████╗██║██║               ║
║   ██║╚██╔╝██║██║   ██║╚════██║██║██║               ║
║   ██║ ╚═╝ ██║╚██████╔╝███████║██║╚██████╗          ║
║   ╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝         ║
║                                                    ║
║        Dark Anime Aesthetic · Fast · Clean         ║
╚════════════════════════════════════════════════════╝
"""

import asyncio
import sys
import os
import importlib
import time

from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.exceptions import NoActiveGroupCall

from config import Config
from database import db, StatsDB
from core.music_manager import music
from utils.logger import get_logger

logger = get_logger("RAXI.MAIN")

# ─── Validate Config ──────────────────────────────────────────────────────────

def validate_config():
    errors = []
    if not Config.API_ID:
        errors.append("API_ID is not set")
    if not Config.API_HASH:
        errors.append("API_HASH is not set")
    if not Config.BOT_TOKEN:
        errors.append("BOT_TOKEN is not set")
    if not Config.STRING_SESSION:
        errors.append("STRING_SESSION is not set")
    if errors:
        for err in errors:
            logger.error(f"❌ Config error: {err}")
        logger.error("Fix your .env file and restart.")
        sys.exit(1)


# ─── Build Pyrogram Clients ───────────────────────────────────────────────────

def create_bot() -> Client:
    return Client(
        "raxi_bot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        plugins=dict(root="plugins"),
    )


def create_userbot() -> Client:
    return Client(
        "raxi_user",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        session_string=Config.STRING_SESSION,
    )


# ─── Load Handlers ────────────────────────────────────────────────────────────

def load_handlers(app: Client):
    from handlers.callbacks import setup as setup_callbacks
    from handlers.errors import setup as setup_errors
    setup_callbacks(app)
    setup_errors(app)
    logger.info("✅ Handlers loaded")


# ─── PyTgCalls Stream End Hook ────────────────────────────────────────────────

def register_call_handlers(call: PyTgCalls, bot: Client):

    @call.on_stream_end()
    async def stream_end_handler(client, update: Update):
        chat_id = update.chat_id
        logger.info(f"🔚 Stream ended in {chat_id}")
        await music.on_stream_end(chat_id)


# ─── Main ─────────────────────────────────────────────────────────────────────

async def main():
    validate_config()

    logger.info("🌑 RAXI MUSIC — Starting up...")
    logger.info("📂 Loading database...")
    await db.load_all()
    await StatsDB.set_start_time()

    logger.info("🤖 Initializing bot client...")
    bot = create_bot()

    logger.info("👤 Initializing userbot client...")
    userbot = create_userbot()

    logger.info("📞 Initializing PyTgCalls...")
    call = PyTgCalls(userbot)

    # Inject into music manager
    music.set_clients(bot, call)

    # Load handlers (callbacks etc.)
    load_handlers(bot)

    # Register stream-end hook
    register_call_handlers(call, bot)

    # Start all clients
    logger.info("🚀 Starting clients...")
    await userbot.start()
    await bot.start()
    await call.start()

    # Get bot info & set invite link
    me = await bot.get_me()
    Config.BOT_USERNAME = me.username or Config.BOT_USERNAME
    Config.BOT_INVITE_LINK = f"https://t.me/{Config.BOT_USERNAME}?startgroup=start"

    logger.info(
        f"✅ RAXI MUSIC is ONLINE\n"
        f"   Bot: @{me.username}\n"
        f"   ID:  {me.id}\n"
        f"   Dark Anime Aesthetic ⚡"
    )

    # Keep alive
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 RAXI MUSIC stopped by user.")
    except Exception as e:
        logger.critical(f"💀 Fatal error: {e}", exc_info=True)
        sys.exit(1)
