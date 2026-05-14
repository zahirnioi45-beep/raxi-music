"""
╔══════════════════════════════════════════════╗
║      RAXI MUSIC - Playback Controls          ║
║   skip · pause · resume · stop · volume      ║
╚══════════════════════════════════════════════╝
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from core.music_manager import music
from database import ChatDB
from utils.decorators import admin_only, maintenance_check
from utils.helpers import format_duration, truncate
from utils.logger import get_logger

logger = get_logger(__name__)


def setup(app: Client):

    @app.on_message(filters.command("skip") & filters.group)
    @maintenance_check
    @admin_only
    async def skip_command(client: Client, message: Message):
        chat_id = message.chat.id
        if not music.is_active(chat_id):
            await message.reply_text("❌ `Tidak ada musik yang sedang diputar.`", quote=True)
            return
        next_track = await music.skip(chat_id)
        if next_track:
            title = truncate(next_track.get("title", "Unknown"), 42)
            dur = format_duration(next_track.get("duration", 0))
            await message.reply_text(
                f"⏭ **Skipped!**\n\n"
                f"🎵 **Now Playing:** `{title}`\n"
                f"🕐 `{dur}`",
                quote=True,
            )
        else:
            await message.reply_text("⏹ **Queue habis.** Bot keluar dari voice chat.", quote=True)

    @app.on_message(filters.command("stop") & filters.group)
    @maintenance_check
    @admin_only
    async def stop_command(client: Client, message: Message):
        chat_id = message.chat.id
        if not music.is_active(chat_id):
            await message.reply_text("❌ `Tidak ada musik yang sedang diputar.`", quote=True)
            return
        await music.stop(chat_id)
        await message.reply_text(
            "⏹ **Stopped.**\n`Musik dihentikan & bot keluar dari voice chat.`",
            quote=True,
        )

    @app.on_message(filters.command("pause") & filters.group)
    @maintenance_check
    @admin_only
    async def pause_command(client: Client, message: Message):
        chat_id = message.chat.id
        if not music.is_playing(chat_id):
            if music.is_paused(chat_id):
                await message.reply_text("⏸ `Musik sudah dalam keadaan pause.`", quote=True)
            else:
                await message.reply_text("❌ `Tidak ada musik yang sedang diputar.`", quote=True)
            return
        ok = await music.pause(chat_id)
        if ok:
            await message.reply_text("⏸ **Paused.**", quote=True)
        else:
            await message.reply_text("❌ `Gagal pause.`", quote=True)

    @app.on_message(filters.command("resume") & filters.group)
    @maintenance_check
    @admin_only
    async def resume_command(client: Client, message: Message):
        chat_id = message.chat.id
        if not music.is_paused(chat_id):
            if music.is_playing(chat_id):
                await message.reply_text("▶️ `Musik sudah berjalan.`", quote=True)
            else:
                await message.reply_text("❌ `Tidak ada musik yang sedang diputar.`", quote=True)
            return
        ok = await music.resume(chat_id)
        if ok:
            await message.reply_text("▶️ **Resumed.**", quote=True)
        else:
            await message.reply_text("❌ `Gagal resume.`", quote=True)

    @app.on_message(filters.command("loop") & filters.group)
    @maintenance_check
    @admin_only
    async def loop_command(client: Client, message: Message):
        chat_id = message.chat.id
        args = message.text.split(maxsplit=1)
        current = ChatDB.get_loop(chat_id)

        mode_map = {"off": "off", "one": "one", "all": "all"}
        label_map = {"off": "❌ Off", "one": "🔂 Single", "all": "🔁 All"}

        if len(args) < 2:
            # Cycle: off → one → all → off
            cycle = {"off": "one", "one": "all", "all": "off"}
            new_mode = cycle.get(current, "off")
        else:
            arg = args[1].lower().strip()
            new_mode = mode_map.get(arg, "off")

        await ChatDB.set_loop(chat_id, new_mode)
        await message.reply_text(
            f"🔁 **Loop Mode:** {label_map[new_mode]}",
            quote=True,
        )

    @app.on_message(filters.command("shuffle") & filters.group)
    @maintenance_check
    @admin_only
    async def shuffle_command(client: Client, message: Message):
        chat_id = message.chat.id
        ok = await music.shuffle_queue(chat_id)
        if ok:
            await message.reply_text("🔀 **Queue di-shuffle!**", quote=True)
        else:
            await message.reply_text("❌ `Queue kosong atau hanya ada 1 lagu.`", quote=True)

    @app.on_message(filters.command("volume") & filters.group)
    @maintenance_check
    @admin_only
    async def volume_command(client: Client, message: Message):
        chat_id = message.chat.id
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            current_vol = ChatDB.get_volume(chat_id)
            await message.reply_text(
                f"🔊 **Volume saat ini:** `{current_vol}%`\n\n"
                "`/volume <1-200>` untuk mengubah volume.",
                quote=True,
            )
            return
        try:
            vol = int(args[1].strip())
        except ValueError:
            await message.reply_text("❌ `Volume harus berupa angka 1–200.`", quote=True)
            return
        ok = await music.set_volume(chat_id, vol)
        if ok:
            vol = max(1, min(200, vol))
            emoji = "🔇" if vol < 20 else "🔉" if vol < 80 else "🔊"
            await message.reply_text(
                f"{emoji} **Volume diatur ke:** `{vol}%`",
                quote=True,
            )
        else:
            await message.reply_text("❌ `Gagal mengubah volume.`", quote=True)
