#!/bin/bash
# ╔══════════════════════════════════════════╗
# ║    RAXI MUSIC - Auto Start Script        ║
# ╚══════════════════════════════════════════╝

DIR="/workspaces/raxi-music"

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
    exit 1
fi

mkdir -p $DIR/{database,cache,downloads}

# ── Install ffmpeg ─────────────────────────────────────────────
if ! command -v ffmpeg &>/dev/null; then
    echo "📦 Installing ffmpeg..."
    sudo apt-get install -y -qq ffmpeg 2>/dev/null && echo "✅ ffmpeg OK"
fi

# ── Pilih Python interpreter (prefer 3.11, fallback 3.10, lalu 3.x) ──
if command -v python3.11 &>/dev/null; then
    PYTHON=python3.11
    echo "🐍 Menggunakan Python 3.11"
elif command -v python3.10 &>/dev/null; then
    PYTHON=python3.10
    echo "🐍 Menggunakan Python 3.10"
else
    PYTHON=python3
    echo "🐍 Menggunakan $(python3 --version)"
fi

VENV="$DIR/venv"

# ── Setup venv ─────────────────────────────────────────────────
if [ ! -f "$VENV/bin/python3" ]; then
    echo "🐍 Creating venv dengan $PYTHON..."
    $PYTHON -m venv $VENV
fi

source $VENV/bin/activate
echo "✅ Python: $(python3 --version)"

# ── Install dependencies ───────────────────────────────────────
if ! python3 -c "import pyrogram" &>/dev/null 2>&1; then
    echo "📦 Installing dependencies..."
    pip install -q --upgrade pip setuptools wheel

    echo "  → pyrogram + TgCrypto..."
    pip install -q "pyrogram==2.0.106" "TgCrypto==1.2.5" || { echo "❌ pyrogram gagal!"; exit 1; }

    echo "  → ntgcalls (binary only, no compile)..."
    pip install -q --only-binary :all: "ntgcalls>=2.0.0" || \
    pip install -q --only-binary :all: ntgcalls || \
    { echo "❌ ntgcalls gagal! Python version mungkin tidak didukung."; exit 1; }

    echo "  → py-tgcalls..."
    pip install -q --no-deps "py-tgcalls>=2.2.11" || { echo "❌ py-tgcalls gagal!"; exit 1; }

    echo "  → other deps..."
    pip install -q yt-dlp aiohttp python-dotenv psutil

    echo "  → verifikasi..."
    python3 -c "import pyrogram; print('  pyrogram ✅')"
    python3 -c "from pytgcalls import PyTgCalls; print('  pytgcalls ✅')" || echo "  pytgcalls ⚠️"
    python3 -c "import yt_dlp; print('  yt-dlp ✅')"
    echo "✅ Dependencies selesai"
else
    echo "✅ Dependencies sudah ada"
fi

echo ""
echo "🚀 Starting RAXI MUSIC..."
echo ""
cd $DIR

CRASH_COUNT=0
while true; do
    python3 main.py
    EXIT=$?
    if [ $EXIT -eq 0 ]; then echo "👋 Bot stopped."; break; fi
    CRASH_COUNT=$((CRASH_COUNT + 1))
    if [ $CRASH_COUNT -ge 5 ]; then echo "❌ Terlalu banyak crash. Cek error di atas."; break; fi
    echo "⚠️  Crash #$CRASH_COUNT — Restart dalam 5 detik..."
    sleep 5
done
