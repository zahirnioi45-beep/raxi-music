"""
╔══════════════════════════════════════════════╗
║       RAXI MUSIC - /play Command             ║
║   Quick Play · Auto Queue · Now Playing UI   ║
╚══════════════════════════════════════════════╝
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from core.music_manager import music
from core.ytdl import ytdl
from core.spotify import spotify
from database import UserDB
from utils.decorators import maintenance_check
from utils.helpers import format_duration, truncate, progress_bar
from utils.logger import get_logger

logger = get_logger(__name__)


def now_playing_markup(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data=f"pause_{chat_id}"),
            InlineKeyboardButton("⏭ Skip", callback_data=f"skip_{chat_id}"),
            InlineKeyboardButton("⏹ Stop", callback_data=f"stop_{chat_id}"),
        ],
        [
            InlineKeyboardButton("📜 Queue", callback_data=f"queue_{chat_id}"),
            InlineKeyboardButton("🔁 Loop", callback_data=f"loop_menu_{chat_id}"),
            InlineKeyboardButton("🔀 Shuffle", callback_data=f"shuffle_{chat_id}"),
        ],
        [
            InlineKeyboardButton("🔉 Vol -10", callback_data=f"vol_down_{chat_id}"),
            InlineKeyboardButton("🔊 Vol +10", callback_data=f"vol_up_{chat_id}"),
        ],
    ])


def queued_markup(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📜 Lihat Queue", callback_data=f"queue_{chat_id}"),
            InlineKeyboardButton("⏭ Skip", callback_data=f"skip_{chat_id}"),
        ]
    ])


def build_now_playing(track: dict, elapsed: int = 0) -> str:
    title = truncate(track.get("title", "Unknown"), 42)
    duration = track.get("duration", 0)
    channel = truncate(track.get("channel", "Unknown"), 25)
    dur_str = format_duration(duration)
    elapsed_str = format_duration(elapsed)
    bar = progress_bar(elapsed, duration) if duration else "━━━━━━━━━━━━"
    source = track.get("source", "youtube").upper()

    return (
        f"🎵 **Now Playing**\n"
        f"╔══════════════════════╗\n"
        f"║  🎶 **{title}**\n"
        f"║  📡 `{source}` · 👤 `{channel}`\n"
        f"║  🕐 `{elapsed_str}` / `{dur_str}`\n"
        f"║  {bar}\n"
        f"╚══════════════════════╝"
    )


def build_queued(track: dict, position: int) -> str:
    title = truncate(track.get("title", "Unknown"), 42)
    dur_str = format_duration(track.get("duration", 0))
    return (
        f"📥 **Added to Queue**\n"
        f"┏ 🎵 **{title}**\n"
        f"┣ 🕐 `{dur_str}`\n"
        f"┗ 📍 Position `#{position}`"
    )


async def resolve_track(query: str) -> dict | None:
    """Resolve query (URL or search) to track dict."""
    # Spotify
    if spotify.is_spotify(query):
        info = await spotify.get_track_info(query)
        if info and info.get("search_query"):
            result = await ytdl.search(info["search_query"])
            if result:
                result["title"] = info.get("title", result["title"])
                result["thumbnail"] = info.get("thumbnail", result.get("thumbnail", ""))
                result["source"] = "spotify"
                return result
    # YouTube or search
    return await ytdl.search(query)


def setup(app: Client):

    @app.on_message(filters.command("play") & filters.group)
    @maintenance_check
    async def play_command(client: Client, message: Message):
        # Register user
        if message.from_user:
            await UserDB.add(
                message.from_user.id,
                message.from_user.first_name or "",
                message.from_user.username or "",
            )

        args = message.text.split(maxsplit=1)

        # Handle audio file
        if message.reply_to_message and message.reply_to_message.audio:
            audio = message.reply_to_message.audio
            searching_msg = await message.reply_text(
                "⬇️ **Downloading audio file...**",
                quote=True,
            )
            try:
                file_path = await message.reply_to_message.download()
                track = {
                    "title": audio.title or audio.file_name or "Audio File",
                    "url": file_path,
                    "duration": audio.duration or 0,
                    "thumbnail": "",
                    "channel": message.from_user.first_name if message.from_user else "User",
                    "source": "file",
                }
            except Exception as e:
                await searching_msg.edit_text(f"❌ **Download failed:** `{e}`")
                return
        elif len(args) < 2:
            await message.reply_text(
                "❓ **Penggunaan:** `/play <judul lagu / URL>`\n\n"
                "**Contoh:**\n"
                "`/play Naruto OST`\n"
                "`/play https://youtu.be/...`\n"
                "`/play https://open.spotify.com/track/...`",
                quote=True,
            )
            return
        else:
            query = args[1].strip()
            searching_msg = await message.reply_text(
                f"🔍 **Mencari:** `{truncate(query, 40)}`...",
                quote=True,
            )
            track = await resolve_track(query)
            if not track:
                await searching_msg.edit_text(
                    f"❌ **Tidak ditemukan:** `{truncate(query, 40)}`\n\n"
                    "Coba judul yang lebih spesifik."
                )
                return

        chat_id = message.chat.id
        result = await music.queue_and_play(chat_id, track)

        if result["status"] == "error":
            await searching_msg.edit_text(
                "❌ **Gagal bergabung ke Voice Chat.**\n"
                "`Pastikan ada aktif Voice Chat di grup ini.`"
            )
            return

        if result["status"] == "playing":
            elapsed = music.elapsed(chat_id)
            await searching_msg.edit_text(
                build_now_playing(track, elapsed),
                reply_markup=now_playing_markup(chat_id),
            )
        elif result["status"] == "queued":
            await searching_msg.edit_text(
                build_queued(track, result["position"]),
                reply_markup=queued_markup(chat_id),
            )
