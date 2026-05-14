"""
RAXI MUSIC - /ping & /stats Commands
"""

import time
from pyrogram import Client, filters
from pyrogram.types import Message
from database import ChatDB, UserDB, StatsDB
from utils.helpers import get_readable_time, human_number
from utils.decorators import maintenance_check


def setup(app: Client):

    @app.on_message(filters.command("ping"))
    @maintenance_check
    async def ping_command(client: Client, message: Message):
        start = time.perf_counter()
        msg = await message.reply_text("🏓 **Pinging...**", quote=True)
        end = time.perf_counter()
        ms = round((end - start) * 1000, 2)

        quality = "🟢 Excellent" if ms < 100 else "🟡 Good" if ms < 300 else "🔴 Slow"

        await msg.edit_text(
            f"🏓 **Pong!**\n\n"
            f"┏ **Response:** `{ms}ms`\n"
            f"┗ **Quality:** {quality}"
        )

    @app.on_message(filters.command("stats"))
    @maintenance_check
    async def stats_command(client: Client, message: Message):
        stats = StatsDB.get()
        uptime_sec = int(time.time()) - stats.get("start_time", int(time.time()))
        uptime_str = get_readable_time(uptime_sec)

        total_chats = ChatDB.count()
        total_users = UserDB.count()
        songs_played = stats.get("songs_played", 0)
        commands_used = stats.get("commands_used", 0)

        await message.reply_text(
            "📊 **RAXI MUSIC — Stats Dashboard**\n"
            "─" * 30 + "\n\n"
            f"┏ ⏱ **Uptime:** `{uptime_str}`\n"
            f"┣ 👥 **Total Chats:** `{human_number(total_chats)}`\n"
            f"┣ 👤 **Total Users:** `{human_number(total_users)}`\n"
            f"┣ 🎵 **Songs Played:** `{human_number(songs_played)}`\n"
            f"┗ ⌨️ **Commands Used:** `{human_number(commands_used)}`\n\n"
            "> Powered by **RAXI SYSTEM** ⚡",
            quote=True,
        )
