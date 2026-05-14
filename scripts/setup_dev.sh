#!/bin/bash
# ╔══════════════════════════════════════╗
# ║  RAXI MUSIC - Dev Environment Setup  ║
# ╚══════════════════════════════════════╝

set -e

echo "🌑 Setting up RAXI MUSIC dev environment..."

# Install ffmpeg
echo "📦 Installing ffmpeg..."
apt-get update -qq && apt-get install -y --no-install-recommends ffmpeg > /dev/null 2>&1
echo "✅ ffmpeg installed"

# Install Python deps
echo "📦 Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "✅ Python dependencies installed"

# Create required dirs
mkdir -p database cache downloads
echo "✅ Directories created"

# Copy .env if not exists
if [ ! -f .env ]; then
    if [ -f sample.env ]; then
        cp sample.env .env
        echo "⚙️  .env created from sample.env — Fill in your credentials!"
    fi
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║  ✅  RAXI MUSIC ready!               ║"
echo "║  1. Fill in .env with your tokens    ║"
echo "║  2. Run: python main.py              ║"
echo "╚══════════════════════════════════════╝"
