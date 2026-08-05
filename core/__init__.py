"""AerostarLens core engine.

Pure-Python, UI-agnostic library. Never imports from ``server/`` or ``ui/`` —
the engine can run headless from a script.

Planned submodules (see ARCHITECTURE.md sections 6-7):
    extract/   Data.p4k -> stock global.ini + DataForge records (scdatatools)
    compose/   DataForge records -> loc-keyed enhancement text
    merge/     source-hierarchy merge engine
    ini/       INI parse / read / write (encoding-tolerant)
    apply/     backup -> validate -> write global.ini, rollback
    patches/   declarative JSON fixes for CIG data bugs
    channels   LIVE/PTU/EPTU/HOTFIX/TECH-PREVIEW isolation + paths
    settings   config, user-data paths, per-channel resolution
    logreader/ Game.log -> the player's own inventory (items, nesting, actions)
"""

__version__ = "0.1.0"
