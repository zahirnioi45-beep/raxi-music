"""
RAXI MUSIC - Command Decorators
"""

import functools
from config import Config
from database import SudoDB, SettingsDB


def owner_only(func):
    @functools.wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        if message.from_user and message.from_user.id == Config.OWNER_ID:
            return await func(client, message, *args, **kwargs)
        await message.reply_text(
            "❌ **Akses Ditolak**\n`Hanya owner yang dapat menggunakan perintah ini.`"
        )
    return wrapper


def sudo_only(func):
    @functools.wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        uid = message.from_user.id if message.from_user else 0
        if uid == Config.OWNER_ID or SudoDB.is_sudo(uid):
            return await func(client, message, *args, **kwargs)
        await message.reply_text(
            "❌ **Akses Ditolak**\n`Hanya sudo user yang dapat menggunakan perintah ini.`"
        )
    return wrapper


def admin_only(func):
    @functools.wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        uid = message.from_user.id if message.from_user else 0
        # Owner & sudo always pass
        if uid == Config.OWNER_ID or SudoDB.is_sudo(uid):
            return await func(client, message, *args, **kwargs)
        try:
            member = await client.get_chat_member(message.chat.id, uid)
            from pyrogram.enums import ChatMemberStatus
            if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                return await func(client, message, *args, **kwargs)
        except Exception:
            pass
        await message.reply_text(
            "❌ **Akses Ditolak**\n`Hanya admin grup yang dapat menggunakan perintah ini.`"
        )
    return wrapper


def maintenance_check(func):
    @functools.wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        uid = message.from_user.id if message.from_user else 0
        if SettingsDB.is_maintenance() and uid != Config.OWNER_ID:
            await message.reply_text(
                "🔧 **Maintenance Mode**\n`Bot sedang dalam pemeliharaan. Coba lagi nanti.`"
            )
            return
        return await func(client, message, *args, **kwargs)
    return wrapper
