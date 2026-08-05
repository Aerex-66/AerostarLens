"""DataForge stage: on-device extraction of the game's structured records.

Chain (verified on a fresh-machine simulation): bundled unp4k pulls Game2.dcb
out of Data.p4k (~10s, 316 MB), bundled unforge converts it to XML records
(~57s, 1.8 GB), then everything except the needed record subtrees is discarded
so the permanent per-channel footprint stays small. Stamped by Data.p4k size —
re-runs only after a game patch.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_VENDOR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2])) / "vendor" / "unp4k"

KEEP_SUBTREES = (
    "libs/foundry/records/missiondata",
    "libs/foundry/records/contracts",
    "libs/foundry/records/missionbroker",
    "libs/foundry/records/missiontype",
    "libs/foundry/records/entities/spaceships",
    "libs/foundry/records/entities/scitem",
    "libs/foundry/records/reputation",
    "libs/foundry/records/factions",
    "libs/foundry/records/ammoparams",
    "libs/foundry/records/ifcs",
    "libs/foundry/records/crafting",
    "libs/foundry/records/mining",
    "libs/foundry/records/resourcetypedatabase",
    "libs/foundry/records/scitemmanufacturer",
    "libs/foundry/records/damage",
    "libs/foundry/records/lootgeneration",
    "libs/foundry/records/consumables",
    "libs/foundry/records/gamerules",
    "libs/foundry/records/tags",
)
_CACHE_VERSION = 4

def dataforge_dir(channel: str) -> Path:
    local = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local")))
    return local / "AerostarLens" / (channel or "LIVE") / "dataforge"

def _stamp(root: Path) -> Path:
    return root / ".stamp.json"

def is_fresh(install_path: str, channel: str) -> bool:
    p4k = Path(install_path) / "Data.p4k"
    root = dataforge_dir(channel)
    if not (p4k.is_file() and root.is_dir() and _stamp(root).is_file()):
        return False
    try:
        data = json.loads(_stamp(root).read_text())
        return data["p4k_size"] == p4k.stat().st_size and data.get("v") == _CACHE_VERSION
    except Exception:
        return False

def _run(args, cwd, timeout):
    return subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        timeout=timeout,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )

def ensure_dataforge(install_path: str, channel: str, progress=None) -> dict:
    """Extract + convert + prune. Returns {ok, dir | error, cached}."""
    say = progress or (lambda _m: None)
    p4k = Path(install_path) / "Data.p4k"
    if not p4k.is_file():
        return {"ok": False, "error": f"Data.p4k not found in {install_path}"}
    root = dataforge_dir(channel)
    if is_fresh(install_path, channel):
        return {"ok": True, "dir": str(root), "cached": True}

    unp4k = _VENDOR / "unp4k.exe"
    unforge = _VENDOR / "unforge.exe"
    if not (unp4k.is_file() and unforge.is_file()):
        return {"ok": False, "error": "Bundled extractor missing"}

    with tempfile.TemporaryDirectory(prefix="lens-df-") as tmp:
        say("Reading mission data from the game (one-time, ~1 min)\u2026")
        r = _run([str(unp4k), str(p4k), "Game2.dcb"], tmp, 900)
        dcb = Path(tmp) / "Data" / "Game2.dcb"
        if r.returncode != 0 or not dcb.is_file():
            return {"ok": False, "error": "DataForge database extraction failed"}

        say("Unpacking game records\u2026")
        r = _run([str(unforge), str(dcb)], str(dcb.parent), 900)
        libs = dcb.parent / "libs"
        if not libs.is_dir():
            return {"ok": False, "error": "DataForge conversion failed"}

        say("Keeping only what Lens needs\u2026")
        if root.is_dir():
            shutil.rmtree(root, ignore_errors=True)
        kept = 0
        for sub in KEEP_SUBTREES:
            src = dcb.parent / Path(sub)
            if src.is_dir():
                dest = root / Path(sub)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dest))
                kept += 1
        if not kept:
            return {"ok": False, "error": "No known record subtrees in DataForge output"}

    root.mkdir(parents=True, exist_ok=True)
    _stamp(root).write_text(json.dumps({"p4k_size": p4k.stat().st_size, "v": _CACHE_VERSION}))
    return {"ok": True, "dir": str(root), "cached": False}
