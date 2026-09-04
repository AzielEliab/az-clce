"""Local UI: loopback only, GET / contains CLCE, score/classify/gate APIs."""

from __future__ import annotations

import json
import threading
import urllib.request

import pytest

from clce.ui import LOOPBACK, make_server
from tests.fixtures import PERFECT


def test_ui_rejects_non_loopback() -> None:
    with pytest.raises(ValueError, match="loopback"):
        make_server("0.0.0.0", 9)
    assert "127.0.0.1" in LOOPBACK


def test_ui_get_root_contains_clce() -> None:
    httpd = make_server("127.0.0.1", 0)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=3) as resp:
            assert resp.status == 200
            html = resp.read().decode("utf-8")
        assert "CLCE" in html
        assert "AZ-CLCE" in html
        assert "cdnjs" not in html.lower() and "unpkg" not in html.lower() and "jsdelivr" not in html.lower()
        assert "inconsistency, not intent" in html.lower() or "Inconsistency, not intent" in html
        assert "What it looks like" in html
        assert "What they wrote" in html
        assert "What it actually does" in html
        assert "Missing pieces" in html
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/style.css", timeout=3) as resp:
            css = resp.read().decode("utf-8")
        assert "c9a227" in css or "--gold" in css
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/score",
            data=json.dumps(PERFECT).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        assert payload["triple"] == 1.0
        assert payload["band"] == "perfect"
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_ui_classify_and_gate_endpoints() -> None:
    httpd = make_server("127.0.0.1", 0)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        body = json.dumps(PERFECT).encode("utf-8")
        for path in ("/api/classify", "/api/gate"):
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}{path}",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            assert payload["triple"] == 1.0
            if path == "/api/gate":
                assert payload["gate"]["passed"] is True
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_ui_import_export_and_health() -> None:
    httpd = make_server("127.0.0.1", 0)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=3) as resp:
            health = json.loads(resp.read().decode("utf-8"))
        assert health["ok"] is True
        assert health["version"] == "0.3.0"
        labeled = (
            "What it looks like (R): login button\n"
            "What they wrote (D): login button\n"
            "What it actually does (P): login button\n"
            "Missing pieces (N):\n"
        )
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/import",
            data=labeled.encode("utf-8"),
            headers={"Content-Type": "text/plain"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            layers = json.loads(resp.read().decode("utf-8"))
        assert layers["r"] == "login button"
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/export",
            data=json.dumps(PERFECT).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        assert payload["report"]["triple"] == 1.0
        assert payload["input_sha256"] in payload["txt"]
        assert "What it looks like (R):" in payload["txt"]
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_ui_rejects_oversized_body() -> None:
    httpd = make_server("127.0.0.1", 0)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        from clce.engine import MAX_BODY_BYTES

        huge = b"x" * (MAX_BODY_BYTES + 8)
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/score",
            data=huge,
            headers={"Content-Type": "application/json", "Content-Length": str(len(huge))},
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(req, timeout=3)
        assert caught.value.code == 413
    finally:
        httpd.shutdown()
        httpd.server_close()
