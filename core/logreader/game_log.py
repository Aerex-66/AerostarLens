"""Locate and read a Star Citizen Game.log (channel-aware, shared read)."""
from __future__ import annotations

import io
from pathlib import Path

CHANNELS = ("LIVE", "PTU", "EPTU", "HOTFIX", "TECH-PREVIEW")

DEFAULT_ROOTS = (
    r"C:\Program Files\Roberts Space Industries\StarCitizen",
    r"D:\Star Citizen Leftovers\StarCitizen",
)

def find_logs(roots=DEFAULT_ROOTS) -> dict:
    """Return ``{(root, channel): Path}`` for every Game.log found."""
    found = {}
    for root in roots:
        base = Path(root)
        if not base.is_dir():
            continue
        for ch in CHANNELS:
            log = base / ch / "Game.log"
            if log.is_file():
                found[(root, ch)] = log
    return found

def newest_log(roots=DEFAULT_ROOTS):
    """Return the most recently written Game.log (the active session), or None."""
    logs = list(find_logs(roots).values())
    if not logs:
        return None
    return max(logs, key=lambda p: p.stat().st_mtime)

def read_text(path) -> str:
    """Read a Game.log the game holds open for writing.

    The game keeps the file open with a shared-read lock, so a normal read
    succeeds. Non-UTF-8 bytes are replaced rather than raising.
    """
    with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()
