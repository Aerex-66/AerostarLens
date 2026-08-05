"""Guarded apply: merge -> backup -> write -> validate -> rollback on mismatch.

Also ensures user.cfg has g_language=english so the game reads the override.
"""
from __future__ import annotations

import shutil
import time
from pathlib import Path

from . import ini
from .compose import compose, needs_dataforge
from .stock import data_root, get_stock

MAX_BACKUPS = 5

def _loc_path(install_path: str) -> Path:
    return Path(install_path) / "data" / "Localization" / "english" / "global.ini"

def _ensure_user_cfg(install_path: str) -> None:
    cfg = Path(install_path) / "user.cfg"
    line = "g_language = english"
    try:
        text = cfg.read_text(encoding="utf-8", errors="replace") if cfg.is_file() else ""
        if "g_language" not in text:
            cfg.write_text((text.rstrip() + "\n" if text.strip() else "") + line + "\n", encoding="utf-8")
    except OSError:
        pass

def _backup(target: Path, channel: str):
    if not target.is_file():
        return None
    backups = data_root(channel) / "backups"
    dest = backups / f"global.{time.strftime('%Y%m%d-%H%M%S')}.ini"
    shutil.copy2(target, dest)
    olds = sorted(backups.glob("global.*.ini"))
    for old in olds[:-MAX_BACKUPS]:
        old.unlink(missing_ok=True)
    return dest

def apply_enhancements(install_path: str, channel: str, enabled: list, progress=None) -> dict:
    """Run the full pipeline. Returns a result dict for the UI."""
    say = progress or (lambda _m: None)
    say("Reading the game's text\u2026")
    stock, base_or_reason = get_stock(install_path, channel)
    if stock is None:
        return {"ok": False, "error": base_or_reason}

    df_dir = None
    if needs_dataforge(enabled):
        from .dataforge import ensure_dataforge

        df = ensure_dataforge(install_path, channel, progress=say)
        if not df.get("ok"):
            return {"ok": False, "error": f"Game data prep failed: {df.get('error')}"}
        df_dir = df["dir"]

    say("Composing enhancements\u2026")
    enhancements = compose(stock, enabled, df_dir)
    merged = dict(stock)
    merged.update(enhancements)

    say("Backing up and writing\u2026")
    target = _loc_path(install_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    backup = _backup(target, channel)

    ini.write(target, merged)

    written = ini.read(target)
    if len(written) < len(stock) or any(k not in written for k in stock):
        if backup:
            shutil.copy2(backup, target)
        else:
            target.unlink(missing_ok=True)
        return {"ok": False, "error": "Validation failed - rolled back"}

    _ensure_user_cfg(install_path)
    return {
        "ok": True,
        "enhanced_keys": len(enhancements),
        "total_keys": len(merged),
        "backup": str(backup) if backup else None,
        "target": str(target),
    }

def restore_localization(install_path: str, channel: str) -> dict:
    """Restore the newest backup, or remove the override to return to vanilla."""
    target = _loc_path(install_path)
    backups = sorted((data_root(channel) / "backups").glob("global.*.ini"))
    if backups:
        shutil.copy2(backups[-1], target)
        return {"ok": True, "restored": str(backups[-1])}
    if target.is_file():
        target.unlink()
        return {"ok": True, "restored": "vanilla (override removed)"}
    return {"ok": True, "restored": "already vanilla"}
