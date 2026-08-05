"""Compose enhancement text keyed by loc-key.

Each category returns {loc_key: appended_block}. Blocks are appended below the
stock description with \\n loc-token line breaks (the game renders them).

`medical` ships first: curated effect text for CureLife consumables — the stock
descriptions are lore-only and never say what the item does. Keys verified
against the extracted stock global.ini (item_Desc<class_name> pattern).
"""
from __future__ import annotations

_MEDICAL_EFFECTS = {
    "crlf_consumable_healing_01": "Heals injuries and restores health (Hemozal). Cures minor Tier 3 injuries.",
    "crlf_consumable_adrenaline_01": "Boosts stamina regen and reduces weapon sway (Demexatrine). Counters exhaustion.",
    "crlf_consumable_oxygen_01": "Instantly refills suit oxygen reserves.",
    "crlf_consumable_painkiller_01": "Suppresses pain symptoms and injury debuffs (Opioca).",
    "crlf_consumable_radiation_01": "Purges radiation buildup (Canoiodide).",
    "crlf_consumable_radiation_02": "Purges heavy radiation buildup; extended duration.",
    "crlf_consumable_gopill_01": "BoostPedia: temporarily raises endurance and sprint recovery.",
    "crlf_consumable_steroids_01": "Corticosteroid: temporarily increases strength and resistance.",
    "crlf_consumable_overdoseRevival_01": "Revives a player downed by drug overdose (Resurgera).",
}

_HEADER = "\\n\\n— AEROSTAR LENS —"

_RULE = "+" + "-" * 26 + "+"

def block(lines, em="EM4", header_em="EM1"):
    """Bordered, emphasis-wrapped block appended below stock text."""
    body = "\\n".join(f"<{header_em}>|</{header_em}> <{em}>{ln}</{em}>" for ln in lines)
    return (
        f"\\n\\n<{header_em}>{_RULE}</{header_em}>"
        f"\\n<{header_em}>|</{header_em}> <{em}>AEROSTAR LENS</{em}>"
        f"\\n{body}"
        f"\\n<{header_em}>{_RULE}</{header_em}>"
    )

def medical(stock: dict) -> dict:
    out = {}
    for cls, effect in _MEDICAL_EFFECTS.items():
        key = f"item_Desc{cls}"
        if key in stock:
            out[key] = stock[key] + block([f"Effect: {effect}"])
    return out

_SURVIVAL_ADVICE = {
    "Hints_ActorStatusHypothermiaStarted": "Fastest fixes: sit in any ship/vehicle seat, stand by a heater or campfire, or equip a cold-rated undersuit (Novikov, Pembroke).",
    "Hints_ActorStatusHypothermiaDamageStarted": "You are TAKING DAMAGE. Board a ship or building now — interiors warm you. A bed heals the injury after.",
    "Hints_ActorStatusHyperthermiaStarted": "Fastest fixes: shade or interiors cool you. Heat-rated undersuits: Calva, Odyssey II. Drink water to slow the buildup.",
    "Hints_ActorStatusHyperthermiaDamageStarted": "You are TAKING DAMAGE. Get indoors or into a ship now, then rehydrate.",
    "Hints_ActorStatusTemperatureBelowMinResistance": "Check your undersuit's temperature rating — every suit lists its min/max. Swap before the debuff starts.",
    "Hints_ActorStatusTemperatureAboveMaxResistance": "Check your undersuit's temperature rating — swap to a heat-rated suit before the debuff starts.",
    "Hints_ActorStatusTemperatureDeath": "Rule of thumb: undersuit rating beats armor. Match the suit to the planet before you leave the ship.",
    "Hints_ActorStatusClothingChanged": "Undersuit ratings are listed on each item — Lens adds the numbers to their descriptions.",
    "Hints_Oxygen1": "OxyPens refill the tank fully and need an undersuit to use. Keep 2 on your leg slots.",
    "Hints_Oxygen2": "An OxyPen refills you instantly — undersuit required.",
    "Hints_Oxygen3": "Use an OxyPen NOW or get to a pressurized room/seat — suffocation knocks you out fast.",
    "Hints_Oxygen4": "Any ship seat or airlock repressurizes you.",
    "Hints_Oxygen6": "Last warning: OxyPen or a pressurized interior immediately.",
    "Hints_Heal1": "MedPen (Hemozal) also cures minor Tier 3 injuries — inject even if not downed.",
    "Hints_Heal2": "Carry pens on armor quick-slots: medical beds cure what pens cannot.",
    "Hints_ActorStatusInjuryStarted": "Check the injury tier in mobiGlas > Vitals. T3 = MedPen. T2/T1 = medical bed or clinic.",
    "Hints_Stamina1": "Overweight gear drains stamina — heavy armor + backpack slows sprinting and aim.",
    "Hints_Stamina2": "An AdrenaPen (Demexatrine) restores stamina instantly in a fight.",
}

def survival(stock: dict) -> dict:
    out = {}
    for key, advice in _SURVIVAL_ADVICE.items():
        if key in stock:
            out[key] = f"{stock[key]} <EM4>— {advice}</EM4>"
    return out

_REGISTRY = {
    "medical": (medical, False),
    "survival": (survival, False),
    "mission_rewards": (None, True),  # resolved lazily to avoid xml import cost
    "components": (None, True),
    "weapons": (None, True),
    "ship_specs": (None, True),
    "armor": (None, True),
}

CATEGORY_IDS = list(_REGISTRY)

def needs_dataforge(enabled: list) -> bool:
    return any(_REGISTRY.get(c, (None, False))[1] for c in enabled)

def compose(stock: dict, enabled: list, df_dir=None) -> dict:
    merged = {}
    for cat in enabled:
        entry = _REGISTRY.get(cat)
        if not entry:
            continue
        composer, needs_df = entry
        if needs_df:
            if not df_dir:
                continue
            if cat == "mission_rewards":
                from .missions import mission_rewards

                merged.update(mission_rewards(stock, df_dir))
            elif cat == "components":
                from .items import components

                merged.update(components(stock, df_dir))
            elif cat == "weapons":
                from .items import weapons

                merged.update(weapons(stock, df_dir))
            elif cat == "ship_specs":
                from .items import ship_specs

                merged.update(ship_specs(stock, df_dir))
            elif cat == "armor":
                from .items import armor

                merged.update(armor(stock, df_dir))
        else:
            merged.update(composer(stock))
    return merged
