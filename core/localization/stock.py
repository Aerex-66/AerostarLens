"""Get the stock global.ini for an install.

Sources, in order:
  1. Per-channel cache (Documents\\AerostarLens\\{CHANNEL}\\cache\\base.ini) when it
     matches the install's current Data.p4k size (patch-freshness stamp).
  2. Extraction from the install's Data.p4k via the bundled unp4k, or an
     scdatatools-capable Python set via AEROSTARLENS_SCDT_PYTHON.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from . import ini

_VENDOR_UNP4K = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2])) / "vendor" / "unp4k" / "unp4k.exe"
_BACKENDS = tuple(p for p in (os.environ.get("AEROSTARLENS_SCDT_PYTHON"),) if p)

_SNIPPET = r"""
import sys
from scdatatools.p4k import P4KFile
p4k = P4KFile(sys.argv[1])
target = 'data/localization/english/global.ini'
match = next((i for i in p4k.infolist() if i.filename.replace('\\', '/').lower() == target), None)
if match is None:
    sys.exit(3)
sys.stdout.buffer.write(p4k.open(match).read())
"""

def data_root(channel: str) -> Path:
    root = Path.home() / "Documents" / "AerostarLens" / (channel or "LIVE")
    (root / "cache").mkdir(parents=True, exist_ok=True)
    (root / "backups").mkdir(parents=True, exist_ok=True)
    return root

def _stamp_path(root: Path) -> Path:
    return root / "cache" / "base.stamp.json"

def _p4k_of(install_path: str) -> Path:
    return Path(install_path) / "Data.p4k"

def _extract_unp4k(p4k: Path, dest: Path) -> bool:
    """Bundled unp4k.exe: extracts to CWD; run in a temp dir and collect the file."""
    if not _VENDOR_UNP4K.is_file():
        return False
    import tempfile

    with tempfile.TemporaryDirectory(prefix="lens-p4k-") as tmp:
        try:
            result = subprocess.run(
                [str(_VENDOR_UNP4K), str(p4k), "english/global.ini"],
                cwd=tmp,
                capture_output=True,
                timeout=600,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            out = Path(tmp) / "Data" / "Localization" / "english" / "global.ini"
            if result.returncode == 0 and out.is_file() and out.stat().st_size > 0:
                dest.write_bytes(out.read_bytes())
                return True
        except Exception:
            pass
    return False

def _extract(p4k: Path, dest: Path) -> bool:
    if _extract_unp4k(p4k, dest):
        return True
    for backend in _BACKENDS:
        if not os.path.isfile(backend):
            continue
        try:
            result = subprocess.run(
                [backend, "-c", _SNIPPET, str(p4k)],
                capture_output=True,
                timeout=300,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            if result.returncode == 0 and result.stdout:
                dest.write_bytes(result.stdout)
                return True
        except Exception:
            continue
    return False

def get_stock(install_path: str, channel: str):
    """Return (entries dict, base_ini_path) or (None, reason string)."""
    p4k = _p4k_of(install_path)
    if not p4k.is_file():
        return None, f"Data.p4k not found in {install_path}"

    root = data_root(channel)
    base = root / "cache" / "base.ini"
    stamp = _stamp_path(root)

    fresh = False
    if base.is_file() and stamp.is_file():
        try:
            fresh = json.loads(stamp.read_text())["p4k_size"] == p4k.stat().st_size
        except Exception:
            fresh = False

    if not fresh:
        if not _extract(p4k, base):
            if not base.is_file():
                return None, "No extraction backend available and no cached base.ini"
        else:
            stamp.write_text(json.dumps({"p4k_size": p4k.stat().st_size}))

    return ini.read(base), str(base)
