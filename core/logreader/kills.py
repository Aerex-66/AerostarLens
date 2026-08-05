"""Kill/death capture from Game.log Actor Death lines.

Format (stable across patches; the standard line community killfeeds parse):
<ts> [Notice] <Actor Death> CActor::Kill: 'Victim' [geid] in zone 'Zone'
killed by 'Killer' [geid] using 'WeaponClass' [Class ...] with damage type 'Type' ...
"""
from __future__ import annotations

import re

from .game_log import read_text
from .history import discover_logs

_RE_KILL = re.compile(
    r"^<([\d:TZ.\-]+)>.*?<Actor Death> CActor::Kill: '([^']+)' \[(\d+)\] in zone '([^']*)'"
    r" killed by '([^']+)' \[(\d+)\] using '([^']*)'.*?damage type '([^']*)'"
)

_RE_NPC = re.compile(r"PU_|NPC|_AI_|Kopion|Quasi|vlk_|_enemy|_soldier|_pilot_|_juggernaut|_grunt|_sniper|Marauder|_civ_|_crew_", re.I)

def _is_npc(name: str) -> bool:
    return bool(_RE_NPC.search(name)) or name.count("_") >= 3

def scan_kills(player_handle=None):
    """All Actor Death events from the newest channel's logs, newest first."""
    metas = []
    for ch, path in discover_logs():
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        metas.append((ch, path, mtime))
    if not metas:
        return {"channel": None, "events": []}
    metas.sort(key=lambda m: m[2])
    target_ch = metas[-1][0]

    events = []
    for ch, path, _m in metas:
        if ch != target_ch:
            continue
        for line in read_text(path).split("\n"):
            m = _RE_KILL.search(line)
            if not m:
                continue
            ts, victim, _vg, zone, killer, _kg, weapon, dtype = m.groups()
            vn, kn = _is_npc(victim), _is_npc(killer)
            if victim == killer:
                kind = "suicide"
            elif not vn and not kn:
                kind = "pvp"
            else:
                kind = "pve"
            events.append(
                {
                    "at": ts,
                    "victim": victim,
                    "killer": killer,
                    "zone": zone,
                    "weapon": weapon,
                    "damage": dtype,
                    "kind": kind,
                    "victim_is_npc": vn,
                    "killer_is_npc": kn,
                    "involves_me": player_handle in (victim, killer) if player_handle else None,
                }
            )
    events.reverse()
    return {"channel": target_ch, "events": events}
