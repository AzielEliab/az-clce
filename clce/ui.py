"""Local AZ-CLCE UI. Bind 127.0.0.1:8845 only.

Three textareas R/D/P, optional N, Score / Classify / Gate.
Shows triple + pairwise + CLCE+ + types + limitation banner.
Self-contained CSS, no CDN, no telemetry.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from urllib.parse import urlparse

from clce.engine import THRESHOLD, gate, score

LOOPBACK = frozenset({"127.0.0.1", "localhost", "::1"})
WEB = files("clce") / "web"
MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}


def _web_bytes(name: str) -> bytes:
    return (WEB / name).read_bytes()


class Handler(BaseHTTPRequestHandler):
    server_version = "AZ-CLCE/0.1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, obj: object) -> None:
        body = json.dumps(obj, indent=2, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            self._send(200, _web_bytes("index.html"), MIME[".html"])
            return
        if path == "/style.css":
            self._send(200, _web_bytes("style.css"), MIME[".css"])
            return
        if path == "/app.js":
            self._send(200, _web_bytes("app.js"), MIME[".js"])
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path not in {"/api/score", "/api/classify", "/api/gate"}:
            self._json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "JSON body required"})
            return
        if not isinstance(payload, dict):
            self._json(400, {"error": "JSON object required"})
            return
        r = str(payload.get("r") or "")
        d = str(payload.get("d") or "")
        p = str(payload.get("p") or "")
        n = str(payload.get("n") or "")
        if path == "/api/gate":
            min_score = payload.get("min", THRESHOLD)
            try:
                min_score = float(min_score)
            except (TypeError, ValueError):
                min_score = THRESHOLD
            passed, report = gate(r=r, d=d, p=p, n=n, min_score=min_score)
            body = report.to_dict()
            body["gate"] = {"min": min_score, "passed": passed}
            self._json(200, body)
            return
        self._json(200, score(r=r, d=d, p=p, n=n).to_dict())


def make_server(host: str = "127.0.0.1", port: int = 8845) -> ThreadingHTTPServer:
    if host not in LOOPBACK:
        raise ValueError("AZ-CLCE UI binds loopback only (127.0.0.1)")
    return ThreadingHTTPServer((host, port), Handler)


def serve(host: str = "127.0.0.1", port: int = 8845) -> None:
    httpd = make_server(host, port)
    bound_host, bound_port = httpd.server_address[:2]
    print(
        f"AZ-CLCE UI http://{bound_host}:{bound_port} "
        "(loopback only; inconsistency, not intent; advisory scores only)"
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        httpd.server_close()
