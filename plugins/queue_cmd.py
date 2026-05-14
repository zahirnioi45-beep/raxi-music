"""
RAXI MUSIC - Queue Command
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from core.music_manager import music
from database import QueueDB
from utils.helpers import format_duration, truncate
from utils.decorators import maintenance_check


def build_queue_text(chat_id: int) -> str:
    current = music.current_track(chat_id)
    queue = QueueDB.get(chat_id)

    lines = ["📜 **QUEUE LIST**\n" + "─" * 28]

    if current:
        title = truncate(current.get("title", "Unknown"), 38)
        dur = format_duration(current.get("duration", 0))
        status = "⏸" if music.is_paused(chat_id) else "▶️"
        lines.append(f"\n{status} **Now Playing**\n`{title}` · `{dur}`")
    else:
        lines.append("\n🚫 _Tidak ada musik yang sedang diputar_")

    if queue:
        lines.append("\n\n**Up Next:**")
        for i, track in enumerate(queue[:10], 1):
            title = truncate(track.get("title", "Unknown"), 35)
            dur = format_duration(track.get("duration", 0))
            lines.append(f"`{i:2d}.` {title} · `{dur}`")
        if len(queue) > 10:
            lines.append(f"\n_...dan {len(queue) - 10} lagu lainnya_")
    else:
        lines.append("\n\n_Queue kosong._")

    lines.append(f"\n\n📊 **Total:** `{len(queue)}` lagu dalam queue")
    return "\n".join(lines)


def setup(app: Client):

    @app.on_message(filters.command("queue") & filters.group)
    @maintenance_check
    async def queue_command(client: Client, message: Message):
        chat_id = message.chat.id
        text = build_queue_text(chat_id)
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔀 Shuffle", callback_data=f"shuffle_{chat_id}"),
                InlineKeyboardButton("🗑 Clear", callback_data=f"clear_queue_{chat_id}"),
                InlineKeyboardButton("❌ Close", callback_data="close_msg"),
            ]
        ])
        await message.reply_text(text, reply_markup=markup, quote=True)
