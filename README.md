# AerostarLens

*See the data the game hides.*

A standalone Windows desktop tool that surfaces Star Citizen data the game already has but never
shows you — mission reputation amounts, component stats, blueprint sources, haul routes — **inside
the game's own UI**, by editing the localization string table (`global.ini`) the game reads on load.

It is **not** an overlay, mod, or memory reader. It edits one text file the game already reads, via
the CIG-sanctioned community-localization path.

> **Status:** pre-alpha, design phase. See [ARCHITECTURE.md](ARCHITECTURE.md) for the full design.

## Part of the Aerostar suite

- **AerostarLens** (this) — user-facing localization enhancer.
- **AerostarGroupPrime** — the React web platform (optional, deferred sync target).

## Stack (planned)

Python core (`scdatatools` extraction) · `pywebview` native shell · React + Vite + Tailwind UI ·
PyInstaller packaging. See [ARCHITECTURE.md](ARCHITECTURE.md).

## Compliance

Localization text only. Extracted game data (`global.ini`, DataForge, and any other Star Citizen file) is CIG-owned,
Unofficial fan project, not affiliated with CIG.
