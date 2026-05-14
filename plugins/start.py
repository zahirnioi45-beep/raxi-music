"""
╔══════════════════════════════════════════════╗
║       RAXI MUSIC - /start Command            ║
║     Dark Anime Aesthetic · Modern UI         ║
╚══════════════════════════════════════════════╝
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import ChatDB, UserDB
from config import Config

START_TEXT = """
╔══════════════════════════════╗
║     🎵  RAXI MUSIC  🎵       ║
║   Dark · Aesthetic · Fast    ║
╚══════════════════════════════╝

┏ **Supported**
┣ 🎵 Music Streaming
┣ 📺 YouTube Links  
┣ 🟢 Spotify Links
┗ 📁 Audio Files

> Powered by **RAXI SYSTEM** ⚡
"""

GROUP_TEXT = """
🎵 **RAXI MUSIC sudah aktif!**

Gunakan `/play <judul lagu>` untuk mulai streaming musik di voice chat.

> Powered by **RAXI SYSTEM** ⚡
"""


def start_buttons(in_group: bool = False) -> InlineKeyboardMarkup:
    if in_group:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("▶️ Play Music", callback_data="play_prompt"),
                InlineKeyboardButton("📖 Commands", callback_data="show_commands"),
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu"),
                InlineKeyboardButton("💸 Donate", callback_data="donate_info"),
            ],
            [
                InlineKeyboardButton(
                    "➕ Tambahkan ke Grup",
                    url=f"https://t.me/{Config.BOT_USERNAME}?startgroup=start"
                ),
            ],
        ])
    else:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("▶️ Play Music", callback_data="play_prompt"),
                InlineKeyboardButton("📖 Commands", callback_data="show_commands"),
            ],
            [
                InlineKeyboardButton("💸 Donate", callback_data="donate_info"),
                InlineKeyboardButton(
                    "➕ Tambahkan ke Grup",
                    url=f"https://t.me/{Config.BOT_USERNAME}?startgroup=start"
                ),
            ],
        ])


def add_to_group_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "➕ Tambahkan RAXI MUSIC ke Grup",
                url=f"https://t.me/{Config.BOT_USERNAME}?startgroup=start"
            )
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="back_start"),
        ]
    ])


async def register_user_and_chat(client: Client, message: Message):
    if message.from_user:
        await UserDB.add(
            message.from_user.id,
            message.from_user.first_name or "",
            message.from_user.username or "",
        )
    if message.chat.type.name != "PRIVATE":
        await ChatDB.add(message.chat.id, message.chat.title or "")


def setup(app: Client):
    @app.on_message(filters.command("start"))
    async def start_command(client: Client, message: Message):
        await register_user_and_chat(client, message)

        in_group = message.chat.type.name != "PRIVATE"
        text = GROUP_TEXT if in_group else START_TEXT

        await message.reply_text(
            text,
            reply_markup=start_buttons(in_group=in_group),
            quote=True,
        )

    @app.on_message(filters.new_chat_members)
    async def on_bot_added(client: Client, message: Message):
        me = await client.get_me()
        for member in message.new_chat_members:
            if member.id == me.id:
                await ChatDB.add(message.chat.id, message.chat.title or "")
                await message.reply_text(
                    GROUP_TEXT,
                    reply_markup=start_buttons(in_group=True),
                )
                break
