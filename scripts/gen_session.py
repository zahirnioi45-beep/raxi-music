"""
╔══════════════════════════════════════════════╗
║     RAXI MUSIC - String Session Generator    ║
║     Jalankan sekali saja untuk generate      ║
║     STRING_SESSION kamu                      ║
╚══════════════════════════════════════════════╝

Cara pakai:
  python scripts/gen_session.py

Nanti akan minta:
  1. API_ID      (dari my.telegram.org)
  2. API_HASH    (dari my.telegram.org)
  3. Nomor HP    (format: +628xxxxxxxx)
  4. Kode OTP    (dikirim via Telegram)

Hasil: STRING_SESSION yang bisa langsung di-copy
"""

import asyncio
from pyrogram import Client


async def main():
    print()
    print("╔══════════════════════════════════════╗")
    print("║   RAXI MUSIC - Session Generator     ║")
    print("╚══════════════════════════════════════╝")
    print()
    print("Ambil API_ID & API_HASH dari: https://my.telegram.org")
    print()

    api_id = input("  Masukkan API_ID     : ").strip()
    api_hash = input("  Masukkan API_HASH   : ").strip()

    if not api_id.isdigit():
        print("\n❌ API_ID harus berupa angka!")
        return

    print()
    print("📱 Sekarang akan minta nomor HP kamu...")
    print("   Format: +628xxxxxxxxxx")
    print()

    async with Client(
        "raxi_gen_session",
        api_id=int(api_id),
        api_hash=api_hash,
    ) as app:
        session = await app.export_session_string()

    print()
    print("╔══════════════════════════════════════╗")
    print("║   ✅ STRING_SESSION BERHASIL!        ║")
    print("╚══════════════════════════════════════╝")
    print()
    print("Copy teks di bawah ini SELURUHNYA:")
    print()
    print("─" * 60)
    print(session)
    print("─" * 60)
    print()
    print("Lalu paste ke GitHub Secrets dengan nama: STRING_SESSION")
    print("Link: https://github.com/zahirnioi45-beep/raxi-music/settings/secrets/codespaces")
    print()

    # Hapus file session sementara
    import os
    for f in ["raxi_gen_session.session", "raxi_gen_session.session-journal"]:
        try:
            os.remove(f)
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
