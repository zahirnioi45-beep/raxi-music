"""
╔══════════════════════════════════════════════╗
║      RAXI MUSIC - Callback Query Handler     ║
║   All inline button actions processed here   ║
╚══════════════════════════════════════════════╝
"""

from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus

from core.music_manager import music
from database import QueueDB, ChatDB, SudoDB
from config import Config
from utils.helpers import format_duration, truncate
from utils.logger import get_logger
from plugins.queue_cmd import build_queue_text
from plugins.play import build_now_playing, now_playing_markup
from plugins.donate import donate_markup, DONATE_TEXT

logger = get_logger(__name__)

COMMANDS_TEXT = """
🎵 **RAXI MUSIC — Command List**
─────────────────────────────

🎵 **Music**
├ `/play` — play musik
├ `/skip` — skip lagu
├ `/stop` — stop musik
├ `/pause` — pause musik
├ `/resume` — resume musik
├ `/queue` — lihat queue
├ `/loop` — loop mode
├ `/shuffle` — shuffle queue
└ `/volume` — atur volume

📖 **Info**
├ `/lyrics` — cari lirik
├ `/ping` — cek kecepatan
├ `/stats` — statistik bot
└ `/donate` — support owner

👑 **Admin Only**
└ skip · stop · pause · resume · volume
"""


def commands_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔙 Back", callback_data="back_start"),
            InlineKeyboardButton("❌ Close", callback_data="close_msg"),
        ]
    ])


def settings_markup(chat_id: int) -> InlineKeyboardMarkup:
    loop = ChatDB.get_loop(chat_id)
    loop_label = {"off": "❌ Off", "one": "🔂 Single", "all": "🔁 All"}.get(loop, "❌ Off")
    vol = ChatDB.get_volume(chat_id)
    mode_247 = "✅ ON" if ChatDB.get_247(chat_id) else "❌ OFF"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"🔁 Loop: {loop_label}", callback_data=f"loop_toggle_{chat_id}"),
        ],
        [
            InlineKeyboardButton(f"🔉 Vol -10", callback_data=f"vol_down_{chat_id}"),
            InlineKeyboardButton(f"🔊 {vol}%", callback_data=f"vol_info_{chat_id}"),
            InlineKeyboardButton(f"🔊 Vol +10", callback_data=f"vol_up_{chat_id}"),
        ],
        [
            InlineKeyboardButton(f"📡 24/7: {mode_247}", callback_data=f"247_toggle_{chat_id}"),
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="back_start"),
            InlineKeyboardButton("❌ Close", callback_data="close_msg"),
        ],
    ])


async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    if user_id == Config.OWNER_ID or SudoDB.is_sudo(user_id):
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False


def setup(app: Client):

    @app.on_callback_query()
    async def handle_callback(client: Client, query: CallbackQuery):
        data = query.data
        user_id = query.from_user.id
        chat_id = query.message.chat.id if query.message else 0

        # ─── Close message ───────────────────────────────────────────────────
        if data == "close_msg":
            await query.message.delete()
            return

        # ─── Back to start ───────────────────────────────────────────────────
        if data == "back_start":
            from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            from plugins.start import start_buttons, START_TEXT, GROUP_TEXT
            in_group = query.message.chat.type.name != "PRIVATE"
            text = GROUP_TEXT if in_group else START_TEXT
            await query.message.edit_text(text, reply_markup=start_buttons(in_group=in_group))
            await query.answer()
            return

        # ─── Show commands ───────────────────────────────────────────────────
        if data == "show_commands":
            await query.message.edit_text(COMMANDS_TEXT, reply_markup=commands_markup())
            await query.answer()
            return

        # ─── Play prompt ─────────────────────────────────────────────────────
        if data == "play_prompt":
            await query.answer(
                "Ketik: /play <judul lagu>",
                show_alert=True,
            )
            return

        # ─── Donate ──────────────────────────────────────────────────────────
        if data == "donate_info":
            await query.message.edit_text(DONATE_TEXT, reply_markup=donate_markup())
            await query.answer()
            return

        # ─── Settings menu ───────────────────────────────────────────────────
        if data == "settings_menu":
            await query.message.edit_text(
                "⚙️ **Settings**\nAtur preferensi musik untuk grup ini.",
                reply_markup=settings_markup(chat_id),
            )
            await query.answer()
            return

        # ─── Controls (require admin) ─────────────────────────────────────────
        if any(data.startswith(p) for p in ("pause_", "skip_", "stop_", "vol_", "shuffle_", "loop_", "clear_queue_", "247_")):
            try:
                target_chat = int(data.split("_")[-1])
            except (ValueError, IndexError):
                await query.answer("❌ Invalid action", show_alert=True)
                return

            admin_ok = await is_admin(client, target_chat, user_id)

            # Pause
            if data.startswith("pause_"):
                if not admin_ok:
                    await query.answer("❌ Hanya admin yang bisa pause.", show_alert=True)
                    return
                if music.is_playing(target_chat):
                    await music.pause(target_chat)
                    await query.answer("⏸ Paused")
                    # Update button
                    markup = InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("▶️ Resume", callback_data=f"resume_{target_chat}"),
                            InlineKeyboardButton("⏭ Skip", callback_data=f"skip_{target_chat}"),
                            InlineKeyboardButton("⏹ Stop", callback_data=f"stop_{target_chat}"),
                        ],
                        [
                            InlineKeyboardButton("📜 Queue", callback_data=f"queue_{target_chat}"),
                            InlineKeyboardButton("🔁 Loop", callback_data=f"loop_menu_{target_chat}"),
                            InlineKeyboardButton("🔀 Shuffle", callback_data=f"shuffle_{target_chat}"),
                        ],
                        [
                            InlineKeyboardButton("🔉 Vol -10", callback_data=f"vol_down_{target_chat}"),
                            InlineKeyboardButton("🔊 Vol +10", callback_data=f"vol_up_{target_chat}"),
                        ],
                    ])
                    try:
                        await query.message.edit_reply_markup(markup)
                    except Exception:
                        pass
                else:
                    await query.answer("❌ Tidak ada yang diputar.", show_alert=True)
                return

            # Resume
            if data.startswith("resume_"):
                if not admin_ok:
                    await query.answer("❌ Hanya admin yang bisa resume.", show_alert=True)
                    return
                if music.is_paused(target_chat):
                    await music.resume(target_chat)
                    await query.answer("▶️ Resumed")
                    try:
                        await query.message.edit_reply_markup(now_playing_markup(target_chat))
                    except Exception:
                        pass
                else:
                    await query.answer("❌ Musik tidak di-pause.", show_alert=True)
                return

            # Skip
            if data.startswith("skip_"):
                if not admin_ok:
                    await query.answer("❌ Hanya admin yang bisa skip.", show_alert=True)
                    return
                next_track = await music.skip(target_chat)
                if next_track:
                    await query.answer(f"⏭ Skipped → {truncate(next_track.get('title',''), 30)}")
                    try:
                        await query.message.edit_text(
                            build_now_playing(next_track, 0),
                            reply_markup=now_playing_markup(target_chat),
                        )
                    except Exception:
                        pass
                else:
                    await query.answer("⏹ Queue habis.")
                    try:
                        await query.message.edit_text("⏹ **Queue habis.** Musik selesai.")
                    except Exception:
                        pass
                return

            # Stop
            if data.startswith("stop_"):
                if not admin_ok:
                    await query.answer("❌ Hanya admin yang bisa stop.", show_alert=True)
                    return
                await music.stop(target_chat)
                await query.answer("⏹ Stopped")
                try:
                    await query.message.edit_text(
                        "⏹ **Musik dihentikan.**\n`Bot keluar dari voice chat.`"
                    )
                except Exception:
                    pass
                return

            # Queue
            if data.startswith("queue_"):
                text = build_queue_text(target_chat)
                markup = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🔀 Shuffle", callback_data=f"shuffle_{target_chat}"),
                        InlineKeyboardButton("🗑 Clear", callback_data=f"clear_queue_{target_chat}"),
                        InlineKeyboardButton("❌ Close", callback_data="close_msg"),
                    ]
                ])
                try:
                    await query.message.edit_text(text, reply_markup=markup)
                except Exception:
                    await query.answer("Queue diperbarui.")
                return

            # Shuffle
            if data.startswith("shuffle_"):
                if not admin_ok:
                    await query.answer("❌ Hanya admin.", show_alert=True)
                    return
                ok = await music.shuffle_queue(target_chat)
                await query.answer("🔀 Queue di-shuffle!" if ok else "❌ Queue kosong.")
                return

            # Clear queue
            if data.startswith("clear_queue_"):
                if not admin_ok:
                    await query.answer("❌ Hanya admin.", show_alert=True)
                    return
                await QueueDB.clear(target_chat)
                await query.answer("🗑 Queue dibersihkan.")
                try:
                    await query.message.edit_text(
                        "🗑 **Queue kosong.**",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("❌ Close", callback_data="close_msg")
                        ]])
                    )
                except Exception:
                    pass
                return

            # Volume down
            if data.startswith("vol_down_"):
                if not admin_ok:
                    await query.answer("❌ Hanya admin.", show_alert=True)
                    return
                current = ChatDB.get_volume(target_chat)
                new_vol = max(1, current - 10)
                await music.set_volume(target_chat, new_vol)
                await query.answer(f"🔉 Volume: {new_vol}%")
                return

            # Volume up
            if data.startswith("vol_up_"):
                if not admin_ok:
                    await query.answer("❌ Hanya admin.", show_alert=True)
                    return
                current = ChatDB.get_volume(target_chat)
                new_vol = min(200, current + 10)
                await music.set_volume(target_chat, new_vol)
                await query.answer(f"🔊 Volume: {new_vol}%")
                return

            # Volume info
            if data.startswith("vol_info_"):
                vol = ChatDB.get_volume(target_chat)
                await query.answer(f"🔊 Volume saat ini: {vol}%", show_alert=True)
                return

            # Loop menu
            if data.startswith("loop_menu_"):
                loop = ChatDB.get_loop(target_chat)
                label = {"off": "❌ Off", "one": "🔂 Single", "all": "🔁 All"}.get(loop, "❌ Off")
                markup = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("❌ Off", callback_data=f"loop_set_off_{target_chat}"),
                        InlineKeyboardButton("🔂 Single", callback_data=f"loop_set_one_{target_chat}"),
                        InlineKeyboardButton("🔁 All", callback_data=f"loop_set_all_{target_chat}"),
                    ],
                    [InlineKeyboardButton("🔙 Back", callback_data=f"back_np_{target_chat}")]
                ])
                try:
                    await query.message.edit_text(
                        f"🔁 **Loop Mode — Saat ini: {label}**\nPilih mode:",
                        reply_markup=markup,
                    )
                except Exception:
                    pass
                await query.answer()
                return

            # Loop set
            if data.startswith("loop_set_"):
                parts = data.split("_")
                # loop_set_off_chatid → parts = ['loop', 'set', 'off', 'chatid']
                mode = parts[2] if len(parts) >= 4 else "off"
                if not admin_ok:
                    await query.answer("❌ Hanya admin.", show_alert=True)
                    return
                await ChatDB.set_loop(target_chat, mode)
                label = {"off": "❌ Off", "one": "🔂 Single", "all": "🔁 All"}.get(mode, "❌ Off")
                await query.answer(f"🔁 Loop: {label}")
                track = music.current_track(target_chat)
                if track:
                    try:
                        await query.message.edit_text(
                            build_now_playing(track, music.elapsed(target_chat)),
                            reply_markup=now_playing_markup(target_chat),
                        )
                    except Exception:
                        pass
                return

            # Loop toggle (from settings)
            if data.startswith("loop_toggle_"):
                if not admin_ok:
                    await query.answer("❌ Hanya admin.", show_alert=True)
                    return
                cycle = {"off": "one", "one": "all", "all": "off"}
                current = ChatDB.get_loop(target_chat)
                new_mode = cycle.get(current, "off")
                await ChatDB.set_loop(target_chat, new_mode)
                label = {"off": "❌ Off", "one": "🔂 Single", "all": "🔁 All"}.get(new_mode)
                await query.answer(f"🔁 Loop: {label}")
                try:
                    await query.message.edit_reply_markup(settings_markup(target_chat))
                except Exception:
                    pass
                return

            # 24/7 toggle
            if data.startswith("247_toggle_"):
                if not admin_ok:
                    await query.answer("❌ Hanya admin.", show_alert=True)
                    return
                current_247 = ChatDB.get_247(target_chat)
                await ChatDB.set_247(target_chat, not current_247)
                state = "✅ ON" if not current_247 else "❌ OFF"
                await query.answer(f"📡 24/7 Mode: {state}")
                try:
                    await query.message.edit_reply_markup(settings_markup(target_chat))
                except Exception:
                    pass
                return

            # Back to now playing
            if data.startswith("back_np_"):
                track = music.current_track(target_chat)
                if track:
                    try:
                        await query.message.edit_text(
                            build_now_playing(track, music.elapsed(target_chat)),
                            reply_markup=now_playing_markup(target_chat),
                        )
                    except Exception:
                        pass
                await query.answer()
                return

        await query.answer()
