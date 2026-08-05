"""Parse a Star Citizen Game.log into the player's own inventory.

Verified log signals (live PTU session):
  <AttachmentReceived> Player[H] Attachment[<inst>, <class>, <geid>]
      items attached to the character (equipped / carried)
  <Update Inventory> ... Persistent Entity[<class>_<geid>, <class>] with Parent[<port path>]
      an item on the body and its NESTED slot path, e.g.
      Body_ItemPort:Armor_Undersuit:Armor_Torso:magazine_attach_5
  <Add Inventory Management Move> Type[Store|Move|Drop|Stack] Source/Target/ItemClass/StoredEntity
      what the player did with an item and where it went
  <Inventory Mgmt Request Queued> for '<H>' [<player geid>] ... Source[<class>] amount[n]
      the player's GEID and per-move quantities

Ownership — keep only the player's own things:
  * an item with a Body_ItemPort parent is on the player -> owned
  * Store/Move keep the item when its target container is not foreign
  * foreign = lootable world crates and NPC gear (Lootable_Container_*, slaver_, kap_)
  * Drop removes the item from the owned set

Commodities / cargo: no commodity-ownership signal appears in an FPS session, so
`commodities` is left empty. The exact cargo/SCU signature needs a hauling session
to confirm before we parse it — deferred on purpose rather than guessed.
"""
from __future__ import annotations

import re
from collections import OrderedDict

from .models import OwnedItem, InventorySnapshot

_RE_ATTACH = re.compile(
    r"<AttachmentReceived> Player\[([^\]]*)\] Attachment\[[^,\]]+,\s*([^,\]]+?)\s*,\s*(\d+)\]"
)
_RE_UPDATE = re.compile(
    r"<Update Inventory>.*?Persistent Entity\[([^,\]]+?),\s*([^\]]+?)\] with Parent\[([^\]]*)\]"
)
_RE_MOVE = re.compile(
    r"<Add Inventory Management Move>.*?Type\[([^\]]*)\].*?SourceInventory\[([^\]]*)\]"
    r".*?TargetInventory\[([^\]]*)\].*?ItemClass\[([^\]]*)\].*?StoredEntity\[([^\]]*)\]"
)
_RE_QUEUED = re.compile(
    r"<Inventory Mgmt Request Queued>.*?for '([^']*)' \[(\d+)\]"
    r".*?Source Inventory\[([^\]]*)\].*?Target Inventory\[([^\]]*)\]\. "
    r"Source\[([^\]]*)\] amount\[(\d+)\]"
)
_RE_INV_DESC = re.compile(r"Inventory\[([A-Za-z0-9_]+?)_(\d{6,}),\s*\2\]")

_RE_SHOP = re.compile(
    r"Send(Shop(?:Buy|Sell)Request).*?shopName\[([^\]]*)\].*?client_price\[([0-9.]+)\].*?itemName\[([^\]]*)\]"
)
_RE_SHOP_TS = re.compile(r"^<([\d:TZ.\-]+)>")
_RE_MISSION_END = re.compile(r"<MissionEnded>.*?mission_id ([0-9a-f\-]{36}) - mission_state (\w+)")

_COSMETIC = re.compile(
    r"head|hair|brow|teeth|eyelash|eyedetail|scalp|mobiglas|visor|necksock|"
    r"facial|_eyes_|^body_|lensdisplay|defaultradar|^Default$|PU_Protos",
    re.I,
)
_FOREIGN = re.compile(r"Lootable_Container|slaver_|^kap_|_npc_|corpse", re.I)

def _geid_of(field: str):
    """'863532255204:Container:0' -> '863532255204'."""
    if not field:
        return None
    return field.split(":", 1)[0] or None

def _entity_id(entity: str):
    """Trailing persistent id: 'ksar_rifle_energy_01_mag_863527755733' -> '863527755733'."""
    if not entity:
        return None
    m = re.search(r"_(\d{6,})$", entity)
    return m.group(1) if m else None

def parse_text(text: str, *, channel=None, source_log=None) -> InventorySnapshot:
    snap = InventorySnapshot(channel=channel, source_log=source_log)
    geid_name: dict[str, str] = {}
    instances: "OrderedDict[str, OwnedItem]" = OrderedDict()
    persistent_classes: set[str] = set()
    attach_seen: list[tuple[str, str]] = []

    def is_foreign(geid) -> bool:
        name = geid_name.get(geid or "")
        return bool(name and _FOREIGN.search(name))

    for line in text.split("\n"):
        if "Inventory[" in line:
            for m in _RE_INV_DESC.finditer(line):
                geid_name[m.group(2)] = m.group(1)

        mq = _RE_QUEUED.search(line)
        if mq:
            snap.player_handle = snap.player_handle or mq.group(1)
            snap.player_geid = snap.player_geid or mq.group(2)

        mu = _RE_UPDATE.search(line)
        if mu:
            ent, cls, port = mu.group(1).strip(), mu.group(2).strip(), mu.group(3).strip()
            if cls and not _COSMETIC.search(cls):
                eid = _entity_id(ent) or ent
                it = instances.get(eid) or OwnedItem(class_name=cls, entity_id=eid)
                it.port_path = port or it.port_path
                if port.startswith("Body_ItemPort"):
                    it.location = "equipped"
                instances[eid] = it
                persistent_classes.add(cls)
            continue

        mm = _RE_MOVE.search(line)
        if mm:
            typ, src, tgt, cls, ent = (g.strip() for g in mm.groups())
            if not cls or _COSMETIC.search(cls):
                continue
            eid = _entity_id(ent)  # only concrete StoredEntity has a persistent id
            if typ == "Drop":
                if eid:
                    instances.pop(eid, None)
                continue
            if not eid or is_foreign(_geid_of(tgt)):
                continue  # NULL-entity moves are actions, not distinct items
            it = instances.get(eid) or OwnedItem(class_name=cls, entity_id=eid)
            it.container_geid = _geid_of(tgt) or _geid_of(src) or it.container_geid
            if it.location == "carried" and typ == "Store":
                it.location = "stored"
            instances[eid] = it
            persistent_classes.add(cls)

        ma = _RE_ATTACH.search(line)
        if ma:
            snap.player_handle = snap.player_handle or ma.group(1)
            cls, ent = ma.group(2).strip(), ma.group(3).strip()
            if cls and not _COSMETIC.search(cls):
                attach_seen.append((cls, ent))

        ms = _RE_SHOP.search(line)
        if ms:
            ts = _RE_SHOP_TS.match(line)
            snap.purchases.append(
                {
                    "kind": "buy" if "Buy" in ms.group(1) else "sell",
                    "shop": ms.group(2),
                    "price": float(ms.group(3)),
                    "item": ms.group(4),
                    "at": ts.group(1) if ts else None,
                }
            )

        mm2 = _RE_MISSION_END.search(line)
        if mm2:
            snap.missions.append({"id": mm2.group(1), "state": mm2.group(2)})

    for cls, ent in attach_seen:
        if cls not in persistent_classes:
            instances.setdefault(ent, OwnedItem(class_name=cls, entity_id=ent, location="equipped"))

    snap.items = list(instances.values())
    return snap
