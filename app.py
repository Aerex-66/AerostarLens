"""AerostarLens — standalone desktop shell.

Opens the UI in a native OS window (pywebview / WebView2) — not a browser.
No address bar, no tabs. A tiny local static server feeds the built React app
to the window; nothing leaves the machine.

Run:
    cd ui && npm run build      # once, produces ui/dist
    python app.py
"""
import functools
import http.server
import os
import socketserver
import sys
import threading

import webview

ROOT = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
UI_DIST = os.path.join(ROOT, "ui", "dist")
PORT = 52788

def _serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=UI_DIST)

    class Threaded(socketserver.ThreadingMixIn, socketserver.TCPServer):
        daemon_threads = True
        allow_reuse_address = True

    with Threaded(("127.0.0.1", PORT), handler) as httpd:
        httpd.serve_forever()

class Api:
    """Native capabilities exposed to the UI as window.pywebview.api."""

    def __init__(self):
        self._progress = None

    def get_progress(self):
        return self._progress

    def pick_folder(self):
        win = webview.windows[0] if webview.windows else None
        if not win:
            return None
        result = win.create_file_dialog(webview.FOLDER_DIALOG)
        return result[0] if result else None

    def game_version(self, install_path):
        """Read the game version (e.g. '4.9.0') from the install's Game.log Env line."""
        try:
            from pathlib import Path
            from core.logreader.history import _peek, fmt_version

            base = Path(install_path)
            log = base / "Game.log"
            if not log.is_file():
                backups = base / "logbackups"
                logs = sorted(backups.glob("*.log"), key=lambda p: p.stat().st_mtime) if backups.is_dir() else []
                log = logs[-1] if logs else None
            if not log:
                return None
            version, _build = _peek(log)
            return fmt_version(version) if version else None
        except Exception:
            return None

    def detect_install(self):
        """Auto-detect the active install: newest channel folder that has a Game.log."""
        try:
            from core.logreader.game_log import newest_log
            from core.logreader.history import _peek, fmt_version

            log = newest_log()
            if not log:
                return None
            version, _build = _peek(log)
            return {
                "path": str(log.parent),
                "channel": log.parent.name.upper(),
                "version": fmt_version(version) if version else None,
            }
        except Exception:
            return None

    def scan_inventory(self):
        """Patch-aware scan of all logs; returns the snapshot dict for the UI."""
        try:
            from core.logreader.history import scan, fmt_version

            snap, info = scan()
            out = snap.to_dict()
            out["patch"] = fmt_version(info.get("target_version"))
            return out
        except Exception:
            return None

    def scan_kills(self):
        """Actor Death events from the active channel's logs, PVP/PVE classified."""
        try:
            from core.logreader.kills import scan_kills

            return scan_kills()
        except Exception:
            return None

    def export_inventory(self):
        """Scan and write the readable JSON export; returns the file path."""
        try:
            import json
            from pathlib import Path

            from core.logreader.history import scan, fmt_version

            snap, info = scan()
            out = snap.to_dict()
            out["patch"] = fmt_version(info.get("target_version"))
            dest_dir = Path.home() / "Documents" / "AerostarLens"
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / "inventory-export.json"
            dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
            return str(dest)
        except Exception:
            return None

    def game_running(self):
        """True when a StarCitizen.exe process is up (works whether the app started first or not)."""
        try:
            import subprocess

            out = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq StarCitizen.exe", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            ).stdout
            return "StarCitizen.exe" in out
        except Exception:
            return False

    def apply_enhancements(self, install_path, channel, enabled):
        """Full localization pipeline: stock -> compose -> merge -> backup -> write -> validate."""
        try:
            from core.localization import apply_enhancements

            def report(msg):
                self._progress = msg

            result = apply_enhancements(install_path, channel or "LIVE", list(enabled or []), progress=report)
            return result
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
        finally:
            self._progress = None

    def restore_localization(self, install_path, channel):
        try:
            from core.localization import restore_localization

            return restore_localization(install_path, channel or "LIVE")
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

def main():
    if not os.path.isfile(os.path.join(UI_DIST, "index.html")):
        raise SystemExit("UI not built. Run:  cd ui && npm run build")

    threading.Thread(target=_serve, daemon=True).start()
    webview.create_window(
        "AerostarLens",
        f"http://127.0.0.1:{PORT}/",
        width=380,
        height=540,
        min_size=(360, 500),
        background_color="#04070E",
        js_api=Api(),
    )
    webview.start()

if __name__ == "__main__":
    main()
