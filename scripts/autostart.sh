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

# ── Generate .env dari Codespaces Secrets ──────────────────────
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

# ── Cek secrets wajib ──────────────────────────────────────────
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
    apt-get install -y -qq ffmpeg 2>/dev/null && echo "✅ ffmpeg installed"
fi

# ── Setup venv ─────────────────────────────────────────────────
if [ ! -f "$VENV/bin/python3" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv $VENV
    echo "✅ venv created"
fi

source $VENV/bin/activate
echo "✅ Python: $(python3 --version)"

# ── Install dependencies ───────────────────────────────────────
if ! python3 -c "import pyrogram" &>/dev/null 2>&1; then
    echo "📦 Installing dependencies (ini butuh ~1-2 menit)..."
    pip install -q --upgrade pip
    pip install -q -r $DIR/requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies sudah ada"
fi

echo ""
echo "🚀 Starting RAXI MUSIC..."
echo ""

cd $DIR

# ── Auto restart jika crash ────────────────────────────────────
while true; do
    python3 main.py
    EXIT=$?
    if [ $EXIT -eq 0 ]; then
        echo "👋 Bot stopped normally."
        break
    fi
    echo "⚠️  Bot crash (exit $EXIT) — Restart dalam 5 detik..."
    sleep 5
done
