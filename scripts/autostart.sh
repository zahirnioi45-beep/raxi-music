#!/bin/bash
# ╔══════════════════════════════════════════╗
# ║    RAXI MUSIC - Auto Start Script        ║
# ║    Generate .env dari Codespaces Secrets ║
# ╚══════════════════════════════════════════╝

echo "🌑 RAXI MUSIC — Auto Start..."

# Generate .env dari environment variables (Codespaces Secrets)
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

echo "✅ .env generated dari Codespaces Secrets"

# Cek wajib
if [ -z "$API_ID" ] || [ -z "$BOT_TOKEN" ] || [ -z "$STRING_SESSION" ]; then
    echo ""
    echo "⚠️  SECRETS BELUM DIISI!"
    echo "Buka: https://github.com/zahirnioi45-beep/raxi-music/settings/secrets/codespaces"
    echo "Tambahkan: API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, OWNER_ID"
    echo ""
    exit 1
fi

# Buat direktori yang dibutuhkan
mkdir -p /workspaces/raxi-music/{database,cache,downloads}

# Install deps kalau belum
pip show pyrogram > /dev/null 2>&1 || {
    echo "📦 Installing dependencies..."
    pip install -q -r /workspaces/raxi-music/requirements.txt
}

echo "🚀 Starting RAXI MUSIC..."
cd /workspaces/raxi-music
python main.py
