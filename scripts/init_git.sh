#!/bin/bash
# ╔══════════════════════════════════════╗
# ║    RAXI MUSIC - Git Init & Push      ║
# ╚══════════════════════════════════════╝

set -e

REPO_URL="${1:-}"

if [ -z "$REPO_URL" ]; then
    echo "Usage: bash scripts/init_git.sh <github-repo-url>"
    echo "Example: bash scripts/init_git.sh https://github.com/yourname/raxi-music.git"
    exit 1
fi

echo "🌑 Initializing RAXI MUSIC git repo..."

git init
git add .
git commit -m "🎵 Initial commit — RAXI MUSIC v1.0

Dark Anime Aesthetic Telegram Music Bot
- Pyrogram + PyTgCalls audio streaming
- Full JSON database (no MongoDB)
- Queue, Loop, Shuffle, Volume
- Inline keyboard UI
- Spotify metadata support
- Admin commands
- Codespaces ready"

git branch -M main
git remote add origin "$REPO_URL"
git push -u origin main

echo ""
echo "✅ Pushed to $REPO_URL"
echo "🚀 Your RAXI MUSIC is now on GitHub!"
