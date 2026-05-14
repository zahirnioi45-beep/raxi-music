<div align="center">

```
██████╗  █████╗ ██╗  ██╗██╗    ███╗   ███╗██╗   ██╗███████╗██╗ ██████╗
██╔══██╗██╔══██╗╚██╗██╔╝██║    ████╗ ████║██║   ██║██╔════╝██║██╔════╝
██████╔╝███████║ ╚███╔╝ ██║    ██╔████╔██║██║   ██║███████╗██║██║
██╔══██╗██╔══██║ ██╔██╗ ██║    ██║╚██╔╝██║██║   ██║╚════██║██║██║
██║  ██║██║  ██║██╔╝ ██╗██║    ██║ ╚═╝ ██║╚██████╔╝███████║██║╚██████╗
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝    ╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝
```

**Dark Anime Aesthetic · Fast · Clean · Production Ready**

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)](https://python.org)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0-green?style=for-the-badge)](https://pyrogram.org)
[![PyTgCalls](https://img.shields.io/badge/PyTgCalls-0.9-purple?style=for-the-badge)](https://pytgcalls.github.io)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## 🎵 Features

- **Audio-Only Streaming** — Voice Chat Telegram (no video, low RAM)
- **Queue System** — Multi-song queue per group
- **Loop Mode** — Off / Single / All
- **Shuffle** — Random queue order
- **Volume Control** — 1–200%
- **Spotify Support** — Metadata fetching, streams via YouTube
- **Lyrics Finder** — Auto-fetch song lyrics
- **24/7 Mode** — Bot stays in VC
- **Full JSON Database** — No MongoDB required
- **Modern Inline UI** — Dark anime aesthetic keyboard
- **➕ Add to Group Button** — One-click add bot to any group
- **Admin Commands** — Broadcast, sudo management, maintenance mode
- **GitHub Codespaces Ready** — Zero-config dev environment

---

## ⚙️ Tech Stack

| Component | Library |
|-----------|---------|
| Bot Framework | `Pyrogram 2.0` |
| Voice Calls | `PyTgCalls 0.9` |
| Audio Source | `yt-dlp` |
| Audio Process | `FFmpeg` |
| HTTP Client | `aiohttp` |
| Database | `JSON (local)` |
| Runtime | `Python 3.11` |

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/yourname/raxi-music.git
cd raxi-music
cp sample.env .env
pip install -r requirements.txt
```

### 2. Configure `.env`

```env
API_ID=12345678
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
STRING_SESSION=your_string_session
OWNER_ID=123456789
```

> **Get STRING_SESSION:** Run the snippet below and paste the output:
> ```python
> from pyrogram import Client
> with Client("session", api_id=API_ID, api_hash=API_HASH) as app:
>     print(app.export_session_string())
> ```

### 3. Run

```bash
python main.py
```

---

## 🐳 Docker

```bash
docker build -t raxi-music .
docker run -d --env-file .env --name raxi-music raxi-music
```

---

## ☁️ GitHub Codespaces

1. Fork this repo
2. Open in Codespaces (green **Code** button → **Codespaces**)
3. Wait for auto-setup (ffmpeg + pip install)
4. Fill in `.env`
5. Run `python main.py`

---

## 📖 Commands

### 🎵 Music
| Command | Description |
|---------|-------------|
| `/play <query>` | Play music (YouTube/Spotify/file) |
| `/skip` | Skip current song |
| `/stop` | Stop and leave VC |
| `/pause` | Pause playback |
| `/resume` | Resume playback |
| `/queue` | Show queue list |
| `/loop` | Toggle loop mode |
| `/shuffle` | Shuffle queue |
| `/volume <1-200>` | Set volume |

### 📖 Info
| Command | Description |
|---------|-------------|
| `/lyrics [title]` | Get song lyrics |
| `/ping` | Bot response time |
| `/stats` | Bot statistics |
| `/donate` | Support owner |

### 👑 Owner/Sudo
| Command | Description |
|---------|-------------|
| `/broadcast` | Broadcast message to all groups |
| `/addsudo <id>` | Add sudo user |
| `/delsudo <id>` | Remove sudo user |
| `/maintenance` | Toggle maintenance mode |
| `/monitor` | System resource monitor |

---

## 🗄️ Database Structure

```
database/
├── chats.json      # Group settings (loop, volume, 24/7)
├── users.json      # User registry
├── queue.json      # Per-chat song queues
├── sudo.json       # Sudo user list
├── stats.json      # Global statistics
└── settings.json   # Bot global settings
```

All writes use **atomic safe-write** (temp file → rename) to prevent corruption.

---

## 📁 Project Structure

```
raxi-music/
├── main.py                 # Entry point
├── config/
│   └── settings.py         # Config from .env
├── core/
│   ├── music_manager.py    # Voice stream controller
│   ├── ytdl.py             # yt-dlp wrapper
│   └── spotify.py          # Spotify metadata
├── database/
│   ├── engine.py           # Async JSON engine
│   └── models.py           # CRUD models
├── plugins/
│   ├── start.py            # /start command
│   ├── play.py             # /play command
│   ├── controls.py         # skip/stop/pause/resume/loop/shuffle/volume
│   ├── queue_cmd.py        # /queue command
│   ├── lyrics_cmd.py       # /lyrics command
│   ├── ping_stats.py       # /ping /stats
│   ├── donate.py           # /donate command
│   └── admin.py            # Admin commands
├── handlers/
│   ├── callbacks.py        # All inline button handlers
│   └── errors.py           # Error handling
├── utils/
│   ├── logger.py           # Logging setup
│   ├── helpers.py          # Format utilities
│   ├── decorators.py       # admin_only, sudo_only, etc.
│   └── lyrics.py           # Lyrics fetcher
├── scripts/
│   ├── setup_dev.sh        # Dev environment setup
│   └── init_git.sh         # Git init & push
├── .devcontainer/
│   └── devcontainer.json   # Codespaces config
├── sample.env              # Environment template
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container image
└── .gitignore
```

---

## 💸 Support

If RAXI MUSIC helps you, consider supporting development!

- [Saweria](https://saweria.co/raxi)
- [Trakteer](https://trakteer.id/raxi)

---

<div align="center">

**Made with ❤️ by RAXI SYSTEM**

*Dark Anime Aesthetic · Fast · Stable · Open Source*

</div>
