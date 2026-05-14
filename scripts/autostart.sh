#!/bin/bash
# ╔══════════════════════════════════════════╗
# ║    RAXI MUSIC - Auto Start Script        ║
# ╚══════════════════════════════════════════╝

DIR="/workspaces/raxi-music"
VENV="$DIR/venv"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   🌑  RAXI MUSIC — Auto Start        ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Generate .env ──────────────────────────────────────────────
cat > $DIR/.env << EOF
API_ID=${API_ID:-}
API_HASH=${API_HASH:-}
BOT_TOKEN=${BOT_TOKEN:-}
STRING_SESSION=${STRING_SESSION:-}
OWNER_ID=${OWNER_ID:-}
OWNER_USERNAME=${OWNER_USERNAME:-}
SUDO_USERS=${SUDO_USERS:-}
BOT_NAME=${BOT_NAME:-RAXI MUSIC}
BOT_USERNAME=${BOT_USERNAME:-raximusic_bot}
SPOTIFY_CLIENT_ID=${SPOTIFY_CLIENT_ID:-}
SPOTIFY_CLIENT_SECRET=${SPOTIFY_CLIENT_SECRET:-}
DONATE_LINK=${DONATE_LINK:-}
TRAKTEER_LINK=${TRAKTEER_LINK:-}
QRIS_LINK=${QRIS_LINK:-}
LOG_LEVEL=${LOG_LEVEL:-INFO}
MAX_QUEUE_SIZE=${MAX_QUEUE_SIZE:-50}
EOF
echo "✅ .env generated"

# ── Cek secrets ────────────────────────────────────────────────
if [ -z "$API_ID" ] || [ -z "$BOT_TOKEN" ] || [ -z "$STRING_SESSION" ]; then
    echo "⚠️  SECRETS BELUM LENGKAP!"
    echo "Buka: https://github.com/zahirnioi45-beep/raxi-music/settings/secrets/codespaces"
    exit 1
fi

# ── Buat direktori ─────────────────────────────────────────────
mkdir -p $DIR/{database,cache,downloads}

# ── Install ffmpeg ─────────────────────────────────────────────
if ! command -v ffmpeg &>/dev/null; then
    echo "📦 Installing ffmpeg..."
    apt-get install -y -qq ffmpeg 2>/dev/null && echo "✅ ffmpeg OK"
fi

# ── Setup venv ─────────────────────────────────────────────────
if [ ! -f "$VENV/bin/python3" ]; then
    echo "🐍 Creating venv..."
    python3 -m venv $VENV
fi

source $VENV/bin/activate
echo "✅ Python: $(python3 --version)"

# ── Install dependencies (dengan error handling) ───────────────
if ! python3 -c "import pyrogram" &>/dev/null 2>&1; then
    echo "📦 Installing dependencies..."

    pip install -q --upgrade pip

    # Install satu per satu agar mudah debug jika ada yang gagal
    echo "  → pyrogram..."
    pip install -q "pyrogram==2.0.106" "TgCrypto==1.2.5" || {
        echo "❌ Gagal install pyrogram!"
        exit 1
    }

    echo "  → pytgcalls..."
    pip install -q "pytgcalls==3.0.0.dev24" || \
    pip install -q "pytgcalls" || {
        echo "❌ Gagal install pytgcalls!"
        exit 1
    }

    echo "  → other deps..."
    pip install -q yt-dlp aiohttp python-dotenv psutil || {
        echo "❌ Gagal install deps lain!"
        exit 1
    }

    # Verifikasi
    python3 -c "import pyrogram; import pytgcalls; print('✅ All imports OK')" || {
        echo "❌ Import check gagal!"
        exit 1
    }
else
    echo "✅ Dependencies sudah ada"
fi

echo ""
echo "🚀 Starting RAXI MUSIC..."
echo ""

cd $DIR

# ── Run bot dengan auto restart ────────────────────────────────
CRASH_COUNT=0
while true; do
    python3 main.py
    EXIT=$?
    if [ $EXIT -eq 0 ]; then
        echo "👋 Bot stopped normally."
        break
    fi
    CRASH_COUNT=$((CRASH_COUNT + 1))
    echo "⚠️  Bot crash #$CRASH_COUNT (exit $EXIT) — Restart dalam 5 detik..."
    # Kalau crash 10x berturut-turut, stop dulu biar tidak spam
    if [ $CRASH_COUNT -ge 10 ]; then
        echo "❌ Terlalu banyak crash. Cek error di atas."
        break
    fi
    sleep 5
done
