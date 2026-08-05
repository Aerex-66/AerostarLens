"""global.ini parse/serialize. Order-preserving, BOM-tolerant, writes UTF-8 BOM
(the encoding the game expects for localization overrides)."""
from __future__ import annotations

def parse(text: str) -> dict:
    """key=value per line; keeps first '=' split; strips ',P' key metadata."""
    out = {}
    for line in text.split("\n"):
        line = line.rstrip("\r")
        if not line.strip() or line.lstrip().startswith(";"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.split(",")[0].strip()
        if key:
            out[key] = value
    return out

def read(path) -> dict:
    with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
        return parse(fh.read())

def write(path, entries: dict) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="\r\n") as fh:
        for key, value in entries.items():
            fh.write(f"{key}={value}\n")
