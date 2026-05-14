#!/bin/bash
# ╔══════════════════════════════════════════╗
# ║    RAXI MUSIC - Auto Start Script        ║
# ╚══════════════════════════════════════════╝

echo "🌑 RAXI MUSIC — Auto Start..."

DIR="/workspaces/raxi-music"

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
    echo "⚠️  SECRETS BELUM DIISI!"
    exit 1
fi

# Buat direktori
mkdir -p $DIR/{database,cache,downloads}

# Install ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "📦 Installing ffmpeg..."
    apk add --no-cache ffmpeg 2>/dev/null || apt-get install -y ffmpeg 2>/dev/null || echo "⚠️ ffmpeg skip"
fi

# Setup virtual environment
if [ ! -d "$DIR/venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv $DIR/venv
fi

# Aktifkan venv
source $DIR/venv/bin/activate
echo "✅ venv aktif: $(python3 --version)"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r $DIR/requirements.txt

echo "🚀 Starting RAXI MUSIC..."
cd $DIR
python3 main.py
