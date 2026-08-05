"""AerostarLens log reader.

Collects the *player's own* inventory from a Star Citizen ``Game.log`` — items,
their nested location, and what the session revealed. Pure standard library.
"""
from .models import OwnedItem, InventorySnapshot
from .parser import parse_text
from .game_log import find_logs, newest_log, read_text, CHANNELS
from .history import scan, discover_logs, fmt_version

def parse_log(path):
    """Read a Game.log at ``path`` and return an :class:`InventorySnapshot`."""
    return parse_text(read_text(path), source_log=str(path))

__all__ = [
    "OwnedItem",
    "InventorySnapshot",
    "parse_text",
    "parse_log",
    "scan",
    "discover_logs",
    "fmt_version",
    "find_logs",
    "newest_log",
    "read_text",
    "CHANNELS",
]
