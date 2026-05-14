"""
RAXI MUSIC - Helper Utilities
"""

import time


def format_duration(seconds: int) -> str:
    """Convert seconds to mm:ss or hh:mm:ss."""
    if not seconds:
        return "00:00"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def truncate(text: str, max_len: int = 35) -> str:
    """Truncate long text with ellipsis."""
    return text[:max_len] + "…" if len(text) > max_len else text


def human_number(n: int) -> str:
    """Format large numbers: 1234 → 1.2K"""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def get_readable_time(seconds: int) -> str:
    """Uptime formatter: 3661 → 1h 1m 1s"""
    result = []
    for unit, label in [(86400, "d"), (3600, "h"), (60, "m"), (1, "s")]:
        val = seconds // unit
        seconds %= unit
        if val:
            result.append(f"{val}{label}")
    return " ".join(result) or "0s"


def progress_bar(current: int, total: int, length: int = 12) -> str:
    """Unicode progress bar."""
    if total == 0:
        return "─" * length
    filled = int(length * current / total)
    bar = "█" * filled + "░" * (length - filled)
    pct = int(100 * current / total)
    return f"{bar} {pct}%"
