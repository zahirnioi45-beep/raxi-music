#!/bin/bash
# ╔══════════════════════════════════════════╗
# ║    RAXI MUSIC - Auto Start Script        ║
# ╚══════════════════════════════════════════╝

echo "🌑 RAXI MUSIC — Auto Start..."

# Generate .env dari Codespaces Secrets
cat > /workspaces/raxi-music/.env << EOF
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

# Cek wajib
if [ -z "$API_ID" ] || [ -z "$BOT_TOKEN" ] || [ -z "$STRING_SESSION" ]; then
    echo "⚠️  SECRETS BELUM DIISI!"
    exit 1
fi

# Buat direktori
mkdir -p /workspaces/raxi-music/{database,cache,downloads}

# Install ffmpeg kalau belum ada
if ! command -v ffmpeg &> /dev/null; then
    echo "📦 Installing ffmpeg..."
    sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg
fi

# Install Python deps pakai python3 -m pip
echo "📦 Installing dependencies..."
python3 -m pip install -q --upgrade pip
python3 -m pip install -q -r /workspaces/raxi-music/requirements.txt

echo "🚀 Starting RAXI MUSIC..."
cd /workspaces/raxi-music
python3 main.py
