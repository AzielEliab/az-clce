"""Local AZ-CLCE UI. Bind 127.0.0.1:8845 only.

Four boxes: What it looks like (R), What they wrote (D),
What it actually does (P), Missing pieces (N).
Giant score, kid-plain result, sample fill, simple/advanced.
Import JSON/txt, export report JSON + human receipt.
Self-contained CSS, no CDN, no telemetry.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from urllib.parse import urlparse

from clce.engine import (
    ENGINE_VERSION,
    MAX_BODY_BYTES,
    THRESHOLD,
    gate,
    score,
)
from clce.io import LayerImportError, parse_layers, receipt_text, report_json_text

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
    server_version = f"AZ-CLCE/{ENGINE_VERSION}"

    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, obj: object) -> None:
        body = json.dumps(obj, indent=2, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _read_body(self) -> bytes | None:
        try:
            length = int(self.headers.get("Content-Length") or "0")
        except ValueError:
            self._json(400, {"error": "invalid Content-Length"})
            return None
        if length < 0:
            self._json(400, {"error": "invalid Content-Length"})
            return None
        if length > MAX_BODY_BYTES:
            self._json(
                413,
                {
                    "error": "payload too large",
                    "limit": MAX_BODY_BYTES,
                    "limitation": "CLCE detects inconsistency, not intent. Type D is a label only.",
                },
            )
            return None
        return self.rfile.read(length) if length else b"{}"

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
        if path == "/api/health":
            self._json(
                200,
                {
                    "ok": True,
                    "version": ENGINE_VERSION,
                    "loopback": True,
                    "telemetry": False,
                    "limitation": (
                        "CLCE detects inconsistency, not intent. "
                        "Type D is a label only."
                    ),
                },
            )
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        allowed = {
            "/api/score",
            "/api/classify",
            "/api/gate",
            "/api/import",
            "/api/export",
        }
        if path not in allowed:
            self._json(404, {"error": "not found"})
            return
        raw = self._read_body()
        if raw is None:
            return
        if path == "/api/import":
            try:
                text = raw.decode("utf-8")
                # Accept either raw text or JSON {"text": "..."} / layers object.
                layers = None
                stripped = text.lstrip("\ufeff").strip()
                if stripped.startswith("{"):
                    try:
                        obj = json.loads(stripped)
                    except json.JSONDecodeError:
                        obj = None
                    if isinstance(obj, dict) and "text" in obj and not any(
                        k in obj for k in ("r", "d", "p", "n", "R", "D", "P", "N")
                    ):
                        layers = parse_layers(str(obj.get("text") or ""))
                    elif isinstance(obj, dict):
                        layers = parse_layers(stripped)
                if layers is None:
                    layers = parse_layers(text)
            except (LayerImportError, ValueError, UnicodeDecodeError) as exc:
                self._json(400, {"error": str(exc)})
                return
            self._json(200, layers)
            return
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "JSON body required"})
            return
        if not isinstance(payload, dict):
            self._json(400, {"error": "JSON object required"})
            return
        try:
            r = str(payload.get("r") or "")
            d = str(payload.get("d") or "")
            p = str(payload.get("p") or "")
            n = str(payload.get("n") or "")
        except Exception as exc:  # noqa: BLE001
            self._json(400, {"error": str(exc)})
            return
        try:
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
            report = score(r=r, d=d, p=p, n=n)
        except ValueError as exc:
            self._json(413 if "size limit" in str(exc) else 400, {"error": str(exc)})
            return
        if path == "/api/export":
            self._json(
                200,
                {
                    "report": report.to_dict(),
                    "json": report_json_text(report),
                    "txt": receipt_text(report),
                    "input_sha256": report.input_sha256,
                    "filename_json": "az-clce-report.json",
                    "filename_txt": "az-clce-receipt.txt",
                },
            )
            return
        self._json(200, report.to_dict())


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
