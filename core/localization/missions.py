"""Mission rewards composer: reads MissionBrokerEntry records and appends the
payout to each mission's description string.

Multiple broker entries (per planet/difficulty) share one description loc key,
so payouts are aggregated into a range. Reputation amounts are GUID-indirected
into records outside the pruned set — they land in a later iteration.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from .compose import block

def _iter_broker(df_dir: Path):
    root = df_dir / "libs" / "foundry" / "records" / "missionbroker"
    if not root.is_dir():
        return
    for xml_path in root.rglob("*.xml"):
        try:
            attrs = ET.parse(xml_path).getroot().attrib
        except ET.ParseError:
            continue
        yield xml_path, attrs

def _payout_of(xml_path: Path) -> int:
    try:
        node = ET.parse(xml_path).getroot().find("missionReward")
        if node is not None and node.attrib.get("currencyType", "UEC") == "UEC":
            return int(float(node.attrib.get("reward", "0")))
    except (ET.ParseError, ValueError):
        pass
    return 0

def _guid_indexes(df_dir: Path, stock: dict):
    """reward guid -> amount; faction guid -> display name (via stock loc key)."""
    amounts, factions = {}, {}
    rep_root = df_dir / "libs" / "foundry" / "records" / "reputation"
    for p in rep_root.rglob("*.xml") if rep_root.is_dir() else []:
        try:
            a = ET.parse(p).getroot().attrib
        except ET.ParseError:
            continue
        if a.get("__type") == "SReputationRewardAmount":
            amounts[a.get("__ref")] = int(float(a.get("reputationAmount", "0")))
    fac_root = df_dir / "libs" / "foundry" / "records" / "factions"
    for p in fac_root.rglob("*.xml") if fac_root.is_dir() else []:
        try:
            a = ET.parse(p).getroot().attrib
        except ET.ParseError:
            continue
        if a.get("__type") == "FactionReputation":
            loc = a.get("displayName", "")
            factions[a.get("__ref")] = stock.get(loc[1:], loc[1:]) if loc.startswith("@") else loc
    return amounts, factions

def _rep_of(xml_path: Path, amounts: dict, factions: dict) -> dict:
    """{faction display name: rep amount} from the first (success) reward list."""
    out = {}
    try:
        node = ET.parse(xml_path).getroot().find("missionResultReputationRewards")
        first = node.find("SReputationAmountListParams") if node is not None else None
        if first is None:
            return out
        for p in first.iter("SReputationAmountParams"):
            fac = factions.get(p.attrib.get("factionReputation"))
            amt = amounts.get(p.attrib.get("reward"), 0)
            if fac and amt:
                out[fac] = max(out.get(fac, 0), amt)
    except ET.ParseError:
        pass
    return out

def mission_rewards(stock: dict, df_dir) -> dict:
    """{desc_loc_key: enhanced text} — payout + rep gains per mission description."""
    df_dir = Path(df_dir)
    amounts, factions = _guid_indexes(df_dir, stock)
    payouts: dict[str, list[int]] = {}
    reps: dict[str, dict] = {}
    givers: dict[str, str] = {}
    buyins: dict[str, list[int]] = {}

    for xml_path, attrs in _iter_broker(df_dir):
        desc = attrs.get("description", "")
        if not desc.startswith("@") or "UNINITIALIZED" in desc or "LOC_EMPTY" in desc:
            continue
        key = desc[1:]
        if key not in stock:
            continue
        amount = _payout_of(xml_path)
        if amount > 0:
            payouts.setdefault(key, []).append(amount)
        for fac, amt in _rep_of(xml_path, amounts, factions).items():
            cur = reps.setdefault(key, {})
            cur[fac] = max(cur.get(fac, 0), amt)
        giver_loc = attrs.get("missionGiver", "")
        if giver_loc.startswith("@") and giver_loc[1:] in stock:
            giver = stock[giver_loc[1:]]
            if "~mission(" not in giver:
                givers.setdefault(key, giver)
        try:
            buyin = int(float(attrs.get("missionBuyInAmount", "0")))
        except ValueError:
            buyin = 0
        if buyin > 0:
            buyins.setdefault(key, []).append(buyin)

    out = {}
    for key in set(payouts) | set(reps) | set(buyins):
        lines = []
        if key in givers:
            lines.append(f"From: {givers[key]}")
        if key in payouts:
            low, high = min(payouts[key]), max(payouts[key])
            lines.append(
                f"Payout: {low:,} aUEC" if low == high
                else f"Payout: {low:,} - {high:,} aUEC ({len(payouts[key])} variants)"
            )
        if key in buyins:
            lines.append(f"Buy-in: {min(buyins[key]):,} aUEC")
        if key in reps:
            rep_txt = " / ".join(f"+{amt:,} {fac}" for fac, amt in sorted(reps[key].items()))
            lines.append(f"Reputation: {rep_txt}")
        out[key] = stock[key] + block(lines, em="EM4")
    return out
