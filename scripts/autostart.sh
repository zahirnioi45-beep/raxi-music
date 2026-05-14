#!/bin/bash
# ╔══════════════════════════════════════════╗
# ║    RAXI MUSIC - Auto Start Script        ║
# ╚══════════════════════════════════════════╝

set -e

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

# Cek secrets wajib
if [ -z "$API_ID" ] || [ -z "$BOT_TOKEN" ] || [ -z "$STRING_SESSION" ]; then
    echo "⚠️  SECRETS BELUM DIISI!"
    exit 1
fi

# Buat direktori
mkdir -p /workspaces/raxi-music/{database,cache,downloads}

# Cari python yang tersedia
PYTHON=""
for cmd in python3.11 python3.10 python3 python; do
    if command -v $cmd &> /dev/null; then
        PYTHON=$cmd
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ Python tidak ditemukan!"
    exit 1
fi
echo "🐍 Menggunakan: $($PYTHON --version)"

# Install pip kalau belum ada
if ! $PYTHON -m pip --version &> /dev/null 2>&1; then
    echo "📦 Installing pip..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | $PYTHON
fi

# Install ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "📦 Installing ffmpeg..."
    apt-get update -qq && apt-get install -y -qq ffmpeg 2>/dev/null || \
    apt install -y ffmpeg 2>/dev/null || \
    echo "⚠️  ffmpeg skip (install manual jika perlu)"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
$PYTHON -m pip install -q --upgrade pip
$PYTHON -m pip install -q -r /workspaces/raxi-music/requirements.txt

echo "🚀 Starting RAXI MUSIC..."
cd /workspaces/raxi-music
$PYTHON main.py
