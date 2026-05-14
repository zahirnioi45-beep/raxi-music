"""
╔══════════════════════════════════════════════╗
║       RAXI MUSIC - Admin Commands            ║
║  broadcast · sudo · maintenance · monitor   ║
╚══════════════════════════════════════════════╝
"""

import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from database import ChatDB, SudoDB, SettingsDB, StatsDB
from utils.decorators import owner_only, sudo_only
from utils.helpers import get_readable_time
from utils.logger import get_logger

logger = get_logger(__name__)


def setup(app: Client):

    # ─── Broadcast ────────────────────────────────────────────────────────────

    @app.on_message(filters.command("broadcast") & filters.private)
    @sudo_only
    async def broadcast_command(client: Client, message: Message):
        if not message.reply_to_message:
            await message.reply_text(
                "📢 **Broadcast**\nReply sebuah pesan untuk di-broadcast.",
                quote=True,
            )
            return

        chats = ChatDB.all()
        total = len(chats)
        success = 0
        failed = 0

        status_msg = await message.reply_text(
            f"📢 **Broadcasting ke {total} grup...**", quote=True
        )

        for chat_id_str in chats:
            try:
                await message.reply_to_message.forward(int(chat_id_str))
                success += 1
            except Exception:
                failed += 1
            await asyncio.sleep(0.05)  # Flood control

        await status_msg.edit_text(
            f"📢 **Broadcast Selesai**\n\n"
            f"┏ ✅ **Sukses:** `{success}`\n"
            f"┗ ❌ **Gagal:** `{failed}`"
        )

    # ─── Sudo Management ──────────────────────────────────────────────────────

    @app.on_message(filters.command("addsudo") & filters.private)
    @owner_only
    async def add_sudo(client: Client, message: Message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply_text(
                "**Usage:** `/addsudo <user_id>`", quote=True
            )
            return
        try:
            uid = int(args[1].strip())
        except ValueError:
            await message.reply_text("❌ `User ID harus berupa angka.`", quote=True)
            return
        await SudoDB.add(uid)
        await message.reply_text(f"✅ **User `{uid}` ditambahkan ke sudo list.**", quote=True)

    @app.on_message(filters.command("delsudo") & filters.private)
    @owner_only
    async def del_sudo(client: Client, message: Message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply_text(
                "**Usage:** `/delsudo <user_id>`", quote=True
            )
            return
        try:
            uid = int(args[1].strip())
        except ValueError:
            await message.reply_text("❌ `User ID harus berupa angka.`", quote=True)
            return
        await SudoDB.remove(uid)
        await message.reply_text(f"✅ **User `{uid}` dihapus dari sudo list.**", quote=True)

    # ─── Maintenance ──────────────────────────────────────────────────────────

    @app.on_message(filters.command("maintenance") & filters.private)
    @owner_only
    async def maintenance_command(client: Client, message: Message):
        current = SettingsDB.is_maintenance()
        new_state = not current
        await SettingsDB.set_maintenance(new_state)
        state_str = "🔧 **ON** — Bot dalam pemeliharaan" if new_state else "✅ **OFF** — Bot aktif normal"
        await message.reply_text(
            f"🔧 **Maintenance Mode:** {state_str}", quote=True
        )

    # ─── Monitor ──────────────────────────────────────────────────────────────

    @app.on_message(filters.command("monitor") & filters.private)
    @sudo_only
    async def monitor_command(client: Client, message: Message):
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            mem_used = mem.used // (1024 * 1024)
            mem_total = mem.total // (1024 * 1024)
            mem_pct = mem.percent
            disk = psutil.disk_usage("/")
            disk_used = disk.used // (1024 * 1024 * 1024)
            disk_total = disk.total // (1024 * 1024 * 1024)
            system_info = (
                f"┣ 🖥 **CPU:** `{cpu}%`\n"
                f"┣ 🧠 **RAM:** `{mem_used}MB / {mem_total}MB ({mem_pct}%)`\n"
                f"┣ 💾 **Disk:** `{disk_used}GB / {disk_total}GB`\n"
            )
        except ImportError:
            system_info = "┣ ⚠️ `psutil not installed`\n"

        stats = StatsDB.get()
        uptime_sec = int(time.time()) - stats.get("start_time", int(time.time()))

        maint_state = "🔧 ON" if SettingsDB.is_maintenance() else "✅ OFF"

        await message.reply_text(
            "🖥 **RAXI MUSIC — Monitor**\n"
            "─" * 28 + "\n\n"
            f"┏ ⏱ **Uptime:** `{get_readable_time(uptime_sec)}`\n"
            f"{system_info}"
            f"┣ 🔧 **Maintenance:** `{maint_state}`\n"
            f"┗ 👥 **Active Chats:** `{ChatDB.count()}`",
            quote=True,
        )
