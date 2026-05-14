FROM python:3.11-slim

LABEL maintainer="RAXI SYSTEM"
LABEL description="RAXI MUSIC — Telegram Voice Chat Music Bot"

# ── System deps ───────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Working dir ───────────────────────────────────────────────────────────────
WORKDIR /app

# ── Python deps ───────────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── App files ─────────────────────────────────────────────────────────────────
COPY . .

# ── Create dirs ───────────────────────────────────────────────────────────────
RUN mkdir -p database cache downloads

# ── Run ───────────────────────────────────────────────────────────────────────
CMD ["python", "main.py"]
