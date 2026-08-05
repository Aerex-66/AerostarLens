"""Scan every Game.log on the machine (current + logbackups) and rebuild the
player's inventory, segmented by patch.

A "patch" is the version token in each log's Env line (e.g. ``sc-alpha-4100`` ->
4.10.0). Star Citizen patches can wipe persistence, so by default only the
*latest* patch's logs are counted — older builds never carry stale items forward.
Pass scope="all" to accumulate every log for the channel regardless of patch.
"""
from __future__ import annotations

import re
from pathlib import Path

from .game_log import CHANNELS, DEFAULT_ROOTS, read_text
from .parser import parse_text
from .models import InventorySnapshot

_RE_ENV = re.compile(r"-sc-[a-z]+-(\d+)-(\d+)", re.I)  # ...-sc-alpha-<version>-<build>-...
_RE_TS = re.compile(r"<([\d:T.\-Z]+)>")
_RE_BUILD_FNAME = re.compile(r"Build\((\d+)\)")

def fmt_version(v):
    """4100 -> '4.10.0', 490 -> '4.9.0'. Falls back to the raw token."""
    if v and v.isdigit() and len(v) >= 3:
        return f"{v[0]}.{int(v[1:-1])}.{v[-1]}"
    return v or "?"

def _peek(path: Path):
    """Read a log's head for its patch version + build (cheap — no full read)."""
    version = build = None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh):
                m = _RE_ENV.search(line)
                if m:
                    version, build = m.group(1), m.group(2)
                    break
                if i > 400:
                    break
    except OSError:
        pass
    if not build:
        fm = _RE_BUILD_FNAME.search(path.name)
        if fm:
            build = fm.group(1)
    return version, build

def discover_logs(roots=DEFAULT_ROOTS, channel=None):
    """Every Game.log + logbackups/*.log on disk, as (channel, Path) pairs."""
    out = []
    for root in roots:
        base = Path(root)
        for ch in [channel] if channel else CHANNELS:
            chdir = base / ch
            if not chdir.is_dir():
                continue
            cur = chdir / "Game.log"
            if cur.is_file():
                out.append((ch, cur))
            backups = chdir / "logbackups"
            if backups.is_dir():
                out.extend((ch, f) for f in backups.glob("*.log"))
    return out

def scan(roots=DEFAULT_ROOTS, channel=None, scope="current"):
    """Rebuild inventory from all logs of the chosen patch.

    Returns (InventorySnapshot, info) where info summarizes what was scanned.
    scope="current" (default) counts only the latest patch; "all" counts every
    log for the latest channel.
    """
    metas = []
    for ch, path in discover_logs(roots, channel):
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        version, build = _peek(path)
        metas.append({"channel": ch, "path": path, "version": version, "build": build, "mtime": mtime})

    metas.sort(key=lambda m: m["mtime"])
    if not metas:
        return InventorySnapshot(), {"logs_scanned": 0, "total_logs": 0, "patches": {}}

    latest = metas[-1]
    tch, tver = latest["channel"], latest["version"]

    if scope == "all":
        chosen = [m for m in metas if m["channel"] == tch]
    else:
        chosen = [m for m in metas if m["channel"] == tch and m["version"] == tver]

    combined = "\n".join(read_text(m["path"]) for m in chosen)
    snap = parse_text(combined, channel=tch, source_log=f"{len(chosen)} logs - patch {fmt_version(tver)}")

    patches = {}
    for m in metas:
        if m["channel"] == tch:
            patches[m["version"]] = patches.get(m["version"], 0) + 1

    info = {
        "target_channel": tch,
        "target_version": tver,
        "logs_scanned": len(chosen),
        "total_logs": len(metas),
        "patches": patches,
    }
    return snap, info
