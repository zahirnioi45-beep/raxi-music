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
import glob

from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls import filters as ptc_filters
from pytgcalls.types import StreamEnded

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


# ─── Load plugins via setup() ─────────────────────────────────────────────────

def load_plugins(app: Client):
    """Load all plugins that have a setup(app) function."""
    plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
    plugin_files = glob.glob(os.path.join(plugin_dir, "*.py"))

    for filepath in sorted(plugin_files):
        name = os.path.basename(filepath)[:-3]
        if name.startswith("_"):
            continue
        try:
            module = importlib.import_module(f"plugins.{name}")
            if hasattr(module, "setup"):
                module.setup(app)
                logger.info(f"✅ Plugin loaded: {name}")
        except Exception as e:
            logger.error(f"❌ Failed to load plugin {name}: {e}")


# ─── Load Handlers ────────────────────────────────────────────────────────────

def load_handlers(app: Client):
    from handlers.callbacks import setup as setup_callbacks
    from handlers.errors import setup as setup_errors
    setup_callbacks(app)
    setup_errors(app)
    logger.info("✅ Handlers loaded")


# ─── PyTgCalls Stream End Hook ────────────────────────────────────────────────

def register_call_handlers(call: PyTgCalls):
    @call.on_update(ptc_filters.stream_end)
    async def stream_end_handler(client: PyTgCalls, update: StreamEnded):
        chat_id = update.chat_id
        logger.info(f"🔚 Stream ended in {chat_id}")
        await music.on_stream_end(chat_id)


# ─── Main ─────────────────────────────────────────────────────────────────────

async def main():
    validate_config()

    logger.info("🌑 RAXI MUSIC — Starting up...")
    await db.load_all()
    await StatsDB.set_start_time()

    # Create clients
    bot = Client(
        "raxi_bot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
    )

    userbot = Client(
        "raxi_user",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        session_string=Config.STRING_SESSION,
    )

    call = PyTgCalls(userbot)

    # Wire up music manager
    music.set_clients(bot, call)

    # Load plugins & handlers
    load_plugins(bot)
    load_handlers(bot)

    # Register stream end hook
    register_call_handlers(call)

    # Start everything
    logger.info("🚀 Starting clients...")
    await userbot.start()
    await bot.start()
    await call.start()

    me = await bot.get_me()
    Config.BOT_USERNAME = me.username or Config.BOT_USERNAME
    Config.BOT_INVITE_LINK = f"https://t.me/{Config.BOT_USERNAME}?startgroup=start"

    logger.info(
        f"\n╔══════════════════════════════════╗\n"
        f"║   ✅  RAXI MUSIC is ONLINE!       ║\n"
        f"║   Bot : @{me.username:<25}║\n"
        f"║   ID  : {me.id:<25} ║\n"
        f"╚══════════════════════════════════╝"
    )

    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 RAXI MUSIC stopped.")
    except Exception as e:
        logger.critical(f"💀 Fatal error: {e}", exc_info=True)
        sys.exit(1)
