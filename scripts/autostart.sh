#!/bin/bash
# ╔══════════════════════════════════════════╗
# ║    RAXI MUSIC - Auto Start Script        ║
# ╚══════════════════════════════════════════╝

DIR="/workspaces/raxi-music"
VENV="$DIR/venv"

echo "🌑 RAXI MUSIC — Auto Start..."

# Generate .env dari Codespaces Secrets
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

# Cek secrets wajib
if [ -z "$API_ID" ] || [ -z "$BOT_TOKEN" ] || [ -z "$STRING_SESSION" ]; then
    echo ""
    echo "⚠️  SECRETS BELUM LENGKAP!"
    echo "Buka: https://github.com/zahirnioi45-beep/raxi-music/settings/secrets/codespaces"
    exit 1
fi

# Buat direktori
mkdir -p $DIR/{database,cache,downloads}

# Setup venv kalau belum ada
if [ ! -f "$VENV/bin/python3" ]; then
    echo "🐍 Creating venv..."
    python3 -m venv $VENV
fi

# Aktifkan venv
source $VENV/bin/activate
echo "✅ venv: $(python3 --version)"

# Install deps kalau belum
if ! python3 -c "import pyrogram" &>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -q --upgrade pip
    pip install -q -r $DIR/requirements.txt
    echo "✅ Dependencies installed"
fi

# Cek ffmpeg
if ! command -v ffmpeg &>/dev/null; then
    echo "📦 Installing ffmpeg..."
    apt-get install -y -qq ffmpeg 2>/dev/null || echo "⚠️ ffmpeg tidak tersedia"
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   🎵  RAXI MUSIC is STARTING...      ║"
echo "╚══════════════════════════════════════╝"
echo ""

cd $DIR

# Jalankan bot — auto restart kalau crash
while true; do
    python3 main.py
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        echo "👋 Bot stopped normally."
        break
    fi
    echo ""
    echo "⚠️  Bot crash (exit $EXIT_CODE) — Restart dalam 5 detik..."
    sleep 5
done
