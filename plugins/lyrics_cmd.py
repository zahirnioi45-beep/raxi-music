"""
RAXI MUSIC - /lyrics Command
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from core.music_manager import music
from utils.lyrics import fetch_lyrics
from utils.decorators import maintenance_check
from utils.helpers import truncate


def setup(app: Client):

    @app.on_message(filters.command("lyrics") & filters.group)
    @maintenance_check
    async def lyrics_command(client: Client, message: Message):
        chat_id = message.chat.id
        args = message.text.split(maxsplit=1)

        if len(args) >= 2:
            query = args[1].strip()
        else:
            track = music.current_track(chat_id)
            if not track:
                await message.reply_text(
                    "❌ `Tidak ada musik. Gunakan /lyrics <judul lagu>`",
                    quote=True,
                )
                return
            query = track.get("title", "")

        msg = await message.reply_text(f"🔍 **Mencari lirik:** `{truncate(query, 40)}`...", quote=True)

        lyrics = await fetch_lyrics(query)
        if not lyrics:
            await msg.edit_text(
                f"❌ **Lirik tidak ditemukan untuk:**\n`{truncate(query, 40)}`"
            )
            return

        # Split if too long
        MAX_LEN = 3900
        header = f"📖 **Lyrics — {truncate(query, 40)}**\n\n"
        if len(lyrics) <= MAX_LEN:
            await msg.edit_text(header + f"```\n{lyrics}\n```")
        else:
            await msg.edit_text(header + f"```\n{lyrics[:MAX_LEN]}\n```\n_...terpotong_")
