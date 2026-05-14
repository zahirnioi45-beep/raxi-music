"""
RAXI MUSIC - /donate Command
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from utils.decorators import maintenance_check


def donate_markup() -> InlineKeyboardMarkup:
    buttons = []

    if Config.DONATE_LINK:
        buttons.append([InlineKeyboardButton("💳 Saweria", url=Config.DONATE_LINK)])
    if Config.TRAKTEER_LINK:
        buttons.append([InlineKeyboardButton("☕ Trakteer", url=Config.TRAKTEER_LINK)])
    if Config.QRIS_LINK:
        buttons.append([InlineKeyboardButton("📲 QRIS", url=Config.QRIS_LINK)])

    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_start")])
    return InlineKeyboardMarkup(buttons)


DONATE_TEXT = """
💸 **Support RAXI MUSIC**

Halo! Terima kasih sudah menggunakan RAXI MUSIC.

Bot ini dibuat dengan ❤️ dan butuh biaya untuk server, domain, dan pengembangan.

Jika kamu suka bot ini, support kita lewat:
┏ 💳 **Saweria**
┣ ☕ **Trakteer**
┗ 📲 **QRIS**

> Setiap donasi sangat berarti! 🙏
"""


def setup(app: Client):

    @app.on_message(filters.command("donate"))
    @maintenance_check
    async def donate_command(client: Client, message: Message):
        await message.reply_text(
            DONATE_TEXT,
            reply_markup=donate_markup(),
            quote=True,
        )
