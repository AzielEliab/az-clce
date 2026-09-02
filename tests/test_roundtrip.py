"""Import JSON/txt roundtrip and receipt sha256 of inputs."""

from __future__ import annotations

import json
from pathlib import Path

from clce.engine import input_sha256, score
from clce.io import load_layers, parse_layers, receipt_text, report_json_text, write_export
from tests.fixtures import PERFECT, TYPE_A, TYPE_D


def test_json_roundtrip_same_sha256(tmp_path: Path) -> None:
    report = score(**TYPE_A)
    json_path, txt_path = write_export(tmp_path / "out.json", report)
    loaded = load_layers(json_path)
    again = score(**loaded)
    assert loaded["r"] == TYPE_A["r"]
    assert loaded["d"] == TYPE_A["d"]
    assert loaded["p"] == TYPE_A["p"]
    assert loaded["n"] == TYPE_A["n"]
    assert again.input_sha256 == report.input_sha256
    assert again.triple == report.triple
    assert report.input_sha256 in txt_path.read_text(encoding="utf-8")
    assert "What it looks like (R):" in txt_path.read_text(encoding="utf-8")


def test_txt_receipt_roundtrip(tmp_path: Path) -> None:
    report = score(**TYPE_D)
    _, txt_path = write_export(tmp_path / "out.json", report)
    from_txt = parse_layers(txt_path.read_text(encoding="utf-8"))
    again = score(**from_txt)
    assert again.input_sha256 == report.input_sha256
    assert again.primary == "D"


def test_parse_labeled_kid_headers() -> None:
    text = (
        "What it looks like (R): blue button\n"
        "What they wrote (D): login form\n"
        "What it actually does (P): login button\n"
        "Missing pieces (N): csrf\n"
    )
    layers = parse_layers(text)
    assert layers["r"] == "blue button"
    assert layers["d"] == "login form"
    assert layers["p"] == "login button"
    assert layers["n"] == "csrf"


def test_parse_json_object() -> None:
    blob = json.dumps({"r": "alpha", "d": "beta", "p": "gamma", "n": ""})
    layers = parse_layers(blob)
    assert layers == {"r": "alpha", "d": "beta", "p": "gamma", "n": ""}


def test_empty_import_ok() -> None:
    layers = parse_layers("{}")
    report = score(**layers)
    assert report.triple == 1.0
    assert report.input_sha256 == input_sha256("", "", "", "")


def test_receipt_contains_limitation_and_kid_plain() -> None:
    report = score(**PERFECT)
    txt = receipt_text(report)
    json_text = report_json_text(report)
    assert "not intent" in txt.lower()
    assert report.kid_plain in txt
    assert report.input_sha256 in txt
    payload = json.loads(json_text)
    assert payload["input_sha256"] == report.input_sha256
    assert payload["schema"] == "az-clce.report.v0.2"
