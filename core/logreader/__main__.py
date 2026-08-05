"""CLI (100% local — no network):
  python -m core.logreader [path-to-Game.log]         one log
  python -m core.logreader --history [--all-patches]   every backup, patch-aware
  python -m core.logreader --export [out.json]         write a readable JSON export
  add --json to print the full snapshot to stdout.
"""
import json
import os
import sys

from . import newest_log, parse_log

def _print_grouped(snap):
    print(f"Player : {snap.player_handle}  [{snap.player_geid}]")
    print(f"Source : {snap.source_log}")
    print(f"Owned  : {len(snap.items)} item instances\n")
    for cls, g in snap.grouped().items():
        print(f"  {g['count']:>3}x  {cls}   ({'/'.join(g['locations'])})")
        for slot in g["slots"]:
            print(f"           - {slot}")

def _default_export_path():
    folder = os.path.join(os.path.expanduser("~"), "Documents", "AerostarLens")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "inventory-export.json")

def main(argv) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    positional = [a for a in argv if not a.startswith("--")]
    export = "--export" in argv
    use_history = "--history" in argv or export

    patch = None
    header = None
    if use_history:
        from .history import scan, fmt_version

        scope = "all" if "--all-patches" in argv else "current"
        snap, info = scan(scope=scope)
        patch = fmt_version(info.get("target_version"))
        seen = ", ".join(f"{fmt_version(k)}x{v}" for k, v in info["patches"].items())
        header = (
            f"Scanned {info['logs_scanned']} of {info['total_logs']} logs "
            f"(channel {info.get('target_channel')}, patch {patch})\n"
            f"Patches on disk: {seen}"
        )
        if scope == "current":
            header += "\n(counting the current patch only; --all-patches to include older)"
    else:
        path = positional[0] if positional else newest_log()
        if not path:
            print("No Game.log found. Pass a path: python -m core.logreader <path>")
            return 1
        snap = parse_log(path)

    if export:
        out = snap.to_dict()
        out["patch"] = patch
        dest = positional[0] if positional else _default_export_path()
        with open(dest, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2)
        print(f"Exported {len(snap.items)} items (patch {patch}) to:\n{dest}")
        return 0
    if "--json" in argv:
        print(json.dumps(snap.to_dict(), indent=2))
        return 0

    if header:
        print(header + "\n")
    _print_grouped(snap)
    if header is None and not snap.commodities:
        print("\nCommodities: none in this session (needs a hauling session).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
