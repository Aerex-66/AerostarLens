"""Item composers: components (shields, quantum drives), weapons, ship basics.

All values read from entity records in the DataForge cache; keys come from each
record's Localization Description attribute. Lines are emitted only when the
stat was actually found — no guesses.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from .compose import block

def _records(root: Path):
    for p in root.rglob("*.xml"):
        try:
            yield ET.parse(p).getroot()
        except ET.ParseError:
            continue

def _loc_desc(rec) -> str | None:
    loc = rec.find(".//Localization")
    if loc is None:
        return None
    d = loc.attrib.get("Description", "")
    return d[1:] if d.startswith("@") and "LOC_" not in d else None

def _attach(rec):
    a = rec.find(".//AttachDef")
    return a.attrib if a is not None else {}

def _emit(stock, out, key, lines, em="EM4"):
    if key and key in stock and lines and key not in out:
        out[key] = stock[key] + block(lines, em=em)

def components(stock: dict, df_dir) -> dict:
    ships_dir = Path(df_dir) / "libs/foundry/records/entities/scitem/ships"
    out = {}
    for rec in _records(ships_dir):
        key = _loc_desc(rec)
        if not key:
            continue
        att = _attach(rec)
        lines = []
        base = []
        if att.get("Size"):
            base.append(f"Size {att['Size']}")
        if att.get("Grade"):
            base.append(f"Grade {att['Grade']}")
        shield = rec.find(".//SCItemShieldGeneratorParams")
        if shield is not None:
            hp = float(shield.attrib.get("MaxShieldHealth", 0))
            rg = float(shield.attrib.get("MaxShieldRegen", 0))
            lines.append(f"Shield: {hp:,.0f} HP · Regen {rg:,.0f}/s")
        qd = rec.find(".//SCItemQuantumDriveParams")
        if qd is not None:
            p = qd.find("params")
            if p is not None:
                speed_km_s = float(p.attrib.get("driveSpeed", 0)) / 1000.0
                lines.append(f"Quantum: {speed_km_s:,.0f} km/s · Cooldown {float(p.attrib.get('cooldownTime', 0)):g}s")
            fuel = float(qd.attrib.get("quantumFuelRequirement", 0))
            if fuel:
                lines.append(f"Fuel: {fuel:g}/Gm")
        if lines:
            if base:
                lines.insert(0, " · ".join(base))
            _emit(stock, out, key, lines)
    return out

def weapons(stock: dict, df_dir) -> dict:
    df = Path(df_dir)
    ammo_dmg = {}
    for rec in _records(df / "libs/foundry/records/ammoparams"):
        ref = rec.attrib.get("__ref")
        dmg_node = rec.find(".//damage")
        total = 0.0
        if dmg_node is not None:
            for child in dmg_node.iter():
                for k, v in child.attrib.items():
                    if k.startswith("Damage"):
                        try:
                            total += float(v)
                        except ValueError:
                            pass
        if ref and total > 0:
            ammo_dmg[ref] = total

    mags = {}
    wp_root = df / "libs/foundry/records/entities/scitem"
    for rec in _records(wp_root / "weapons"):
        cont = rec.find(".//SAmmoContainerComponentParams")
        if cont is not None and rec.attrib.get("__ref"):
            mags[rec.attrib["__ref"]] = (
                int(float(cont.attrib.get("maxAmmoCount", 0))),
                cont.attrib.get("ammoParamsRecord"),
            )

    out = {}
    for rec in _records(wp_root / "weapons"):
        wpn = rec.find(".//SCItemWeaponComponentParams")
        if wpn is None:
            continue
        key = _loc_desc(rec)
        if not key:
            continue
        lines = []
        rates = []
        for fire in rec.iter():
            if fire.tag.startswith("SWeaponActionFire") and fire.attrib.get("fireRate", "0") not in ("0", ""):
                rates.append(int(float(fire.attrib["fireRate"])))
        if rates:
            lines.append(f"Fire rate: {max(rates)} rpm")
        mag = mags.get(wpn.attrib.get("ammoContainerRecord", ""))
        dmg = None
        if mag:
            cap, ammo_ref = mag
            if cap:
                lines.append(f"Magazine: {cap}")
            dmg = ammo_dmg.get(ammo_ref or "")
        if dmg:
            lines.append(f"Damage/shot: {dmg:g}")
            if rates:
                lines.append(f"DPS: {dmg * max(rates) / 60:,.0f}")
        _emit(stock, out, key, lines)
    return out

def ship_specs(stock: dict, df_dir) -> dict:
    out = {}
    for rec in _records(Path(df_dir) / "libs/foundry/records/entities/spaceships"):
        key = _loc_desc(rec)
        if not key:
            continue
        lines = []
        disp = rec.find(".//displayParams")
        if disp is not None:
            crew = disp.attrib.get("crewSize", "")
            if crew and crew != "0":
                lines.append(f"Crew: {crew}")
        buy = rec.find(".//SCItemPurchasableParams")
        if buy is not None:
            cls = buy.attrib.get("displayType", "")
            if cls.startswith("@") and cls[1:] in stock:
                lines.append(f"Class: {stock[cls[1:]]}")
        _emit(stock, out, key, lines)
    return out

def armor(stock: dict, df_dir) -> dict:
    """FPS armor + undersuits: temperature rating (the dress-for-the-planet line)."""
    out = {}
    root = Path(df_dir) / "libs/foundry/records/entities/scitem/characters/human/armor"
    for rec in _records(root):
        key = _loc_desc(rec)
        if not key:
            continue
        lines = []
        tr = rec.find(".//TemperatureResistance")
        if tr is not None:
            lo, hi = tr.attrib.get("MinResistance"), tr.attrib.get("MaxResistance")
            if lo is not None and hi is not None:
                lines.append(f"Temp rating: {float(lo):g} to {float(hi):g} degC")
        att = _attach(rec)
        if att.get("SubType") and att["SubType"] != "UNDEFINED":
            lines.append(f"Type: {att['SubType']}")
        _emit(stock, out, key, lines)
    return out
