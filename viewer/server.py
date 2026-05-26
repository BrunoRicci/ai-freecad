#!/usr/bin/env python3
"""
Lightweight dev server for the furniture 3D viewer.

  python viewer/server.py          # port 8080
  python viewer/server.py 3000     # custom port

Open http://localhost:<port> in your browser.
Edit viewer/spec.py or furniture_tool/config.py — viewer auto-updates in ~2 s.
"""
import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT       = Path(__file__).resolve().parent.parent
VIEWER_DIR = Path(__file__).resolve().parent
EXPORTER   = ROOT / "furniture_tool" / "geometry_exporter.py"

WATCH = [
    ROOT / "furniture_tool" / "config.py",
    ROOT / "furniture_tool" / "solver.py",
    VIEWER_DIR / "spec.py",
]

_cache: dict = {"body": None, "mtime": 0.0}


def _source_mtime() -> float:
    t = 0.0
    for p in WATCH:
        try:
            t = max(t, p.stat().st_mtime)
        except FileNotFoundError:
            pass
    return t


def geometry_json() -> bytes:
    mtime = _source_mtime()
    if _cache["body"] is None or mtime > _cache["mtime"]:
        result = subprocess.run(
            [sys.executable, str(EXPORTER)],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        if result.returncode == 0 and result.stdout.strip():
            raw = result.stdout.strip()
        else:
            raw = json.dumps({"ok": False, "error": result.stderr or "exporter crashed"})
        _cache["body"] = raw.encode()
        _cache["mtime"] = mtime
    return _cache["body"]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._serve(VIEWER_DIR / "index.html", "text/html; charset=utf-8")
        elif self.path == "/geometry.json":
            body = geometry_json()
            self._respond(200, "application/json", body)
        else:
            self._respond(404, "text/plain", b"not found")

    def _serve(self, path: Path, ctype: str):
        try:
            self._respond(200, ctype, path.read_bytes())
        except FileNotFoundError:
            self._respond(404, "text/plain", b"file not found")

    def _respond(self, code: int, ctype: str, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):  # silence request noise
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"Furniture viewer → http://localhost:{port}")
    print("Edit viewer/spec.py or furniture_tool/config.py to update the model.")
    print("Ctrl-C to stop.\n")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
