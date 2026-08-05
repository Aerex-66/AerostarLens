"""Data models for the log reader."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class OwnedItem:
    """One instance of an item the player owns, as seen in the log."""

    class_name: str
    entity_id: Optional[str] = None
    quantity: int = 1
    port_path: Optional[str] = None          # nested slot path on the body, ':'-delimited
    container_geid: Optional[str] = None
    location: str = "carried"                # carried | stored | equipped
    display_name: Optional[str] = None       # resolved later via sc_general_items

@dataclass
class InventorySnapshot:
    """Everything the session told us about the player's own inventory."""

    player_handle: Optional[str] = None
    player_geid: Optional[str] = None
    channel: Optional[str] = None
    source_log: Optional[str] = None
    items: list = field(default_factory=list)         # list[OwnedItem]
    commodities: list = field(default_factory=list)   # reserved — see parser notes
    purchases: list = field(default_factory=list)     # shop buy/sell events {kind, shop, price, item, at}
    missions: list = field(default_factory=list)      # MissionEnded events {id, state}

    def grouped(self) -> dict:
        """Aggregate instances by item class -> {count, locations, nesting slots}."""
        out: dict[str, dict] = {}
        for it in self.items:
            g = out.setdefault(it.class_name, {"count": 0, "locations": set(), "slots": set()})
            g["count"] += 1
            g["locations"].add(it.location)
            if it.port_path:
                g["slots"].add(it.port_path)
        return {
            cls: {
                "count": g["count"],
                "locations": sorted(g["locations"]),
                "slots": sorted(g["slots"]),
            }
            for cls, g in sorted(out.items(), key=lambda kv: -kv[1]["count"])
        }

    def to_dict(self) -> dict:
        return {
            "player_handle": self.player_handle,
            "player_geid": self.player_geid,
            "channel": self.channel,
            "source_log": self.source_log,
            "item_count": len(self.items),
            "items_by_class": self.grouped(),
            "commodities": self.commodities,
            "purchases": self.purchases,
            "missions_completed": sum(1 for m in self.missions if "COMPLETED" in m.get("state", "")),
            "missions": self.missions,
        }
