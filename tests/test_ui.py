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
