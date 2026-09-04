"""Self-check for AZ-CLCE. NASA-robust, no network, no telemetry.

    clce doctor
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Callable

from clce import __version__
from clce.engine import (
    ENGINE_VERSION,
    MAX_BODY_BYTES,
    MAX_FIELD_CHARS,
    debug_enabled,
    score,
)
from clce.io import load_layers, parse_layers, write_export
from clce.ui import LOOPBACK, make_server

# Inline fixtures — doctor must not import tests/ (not installed at runtime).
_PERFECT = {
    "r": "login button submit credentials",
    "d": "login button submit credentials",
    "p": "login button submit credentials",
    "n": "",
}
_TYPE_A = {
    "r": "login button blue icon",
    "d": "login form green label",
    "p": "login button form works",
    "n": "",
}
_TYPE_B = {
    "r": "login button submit",
    "d": "login button submit",
    "p": "crash error timeout",
    "n": "",
}
_TYPE_C = {
    "r": "alpha beta gamma delta",
    "d": "gamma delta epsilon zeta",
    "p": "epsilon zeta eta theta",
    "n": "",
}
_TYPE_D = {
    "r": "secure login form",
    "d": "secure login form",
    "p": "open redirect leak",
    "n": "csrf session timeout encryption audit",
}

Check = tuple[str, bool, str]


def _ok(name: str, detail: str = "") -> Check:
    return name, True, detail


def _fail(name: str, detail: str) -> Check:
    return name, False, detail


def _check_version() -> Check:
    if __version__ == ENGINE_VERSION == "0.3.0":
        return _ok("version", __version__)
    return _fail("version", f"{__version__} vs engine {ENGINE_VERSION}")


def _check_empty() -> Check:
    report = score("", "", "", "")
    if report.triple == 1.0 and report.band == "perfect":
        return _ok("empty fields", "triple=1.0 (empty is OK)")
    return _fail("empty fields", f"triple={report.triple} band={report.band}")


def _check_perfect() -> Check:
    report = score(**_PERFECT)
    if report.triple == 1.0 and report.types == ():
        return _ok("perfect fixture", f"sha256={report.input_sha256[:12]}…")
    return _fail("perfect fixture", f"triple={report.triple} types={report.types}")


def _check_types() -> Check:
    got = {
        "A": "A" in score(**_TYPE_A).types,
        "B": "B" in score(**_TYPE_B).types,
        "C": "C" in score(**_TYPE_C).types,
        "D": score(**_TYPE_D).primary == "D",
    }
    if all(got.values()):
        return _ok("types A-D", "D is a label only")
    return _fail("types A-D", str(got))


def _check_loopback() -> Check:
    if "127.0.0.1" not in LOOPBACK:
        return _fail("loopback", "127.0.0.1 missing from LOOPBACK")
    try:
        make_server("0.0.0.0", 9)
    except ValueError as exc:
        if "loopback" in str(exc).lower():
            return _ok("loopback", "rejects 0.0.0.0")
        return _fail("loopback", str(exc))
    return _fail("loopback", "make_server accepted 0.0.0.0")


def _check_size_limits() -> Check:
    try:
        score(r="x" * (MAX_FIELD_CHARS + 1))
    except ValueError as exc:
        if "size limit" in str(exc):
            return _ok(
                "size limits",
                f"field={MAX_FIELD_CHARS} body={MAX_BODY_BYTES}",
            )
        return _fail("size limits", str(exc))
    return _fail("size limits", "oversized field was accepted")


def _check_roundtrip() -> Check:
    report = score(**_TYPE_A)
    with tempfile.TemporaryDirectory() as tmp:
        json_path, txt_path = write_export(Path(tmp) / "report.json", report)
        loaded = load_layers(json_path)
        again = score(**loaded)
        from_txt = parse_layers(txt_path.read_text(encoding="utf-8"))
        txt_again = score(**from_txt)
        if (
            again.input_sha256 == report.input_sha256
            and txt_again.input_sha256 == report.input_sha256
            and report.input_sha256 in txt_path.read_text(encoding="utf-8")
        ):
            return _ok("import/export roundtrip", report.input_sha256[:12] + "…")
        return _fail(
            "import/export roundtrip",
            f"json={again.input_sha256} txt={txt_again.input_sha256} orig={report.input_sha256}",
        )


def _check_web() -> Check:
    from importlib.resources import files

    html = (files("clce") / "web" / "index.html").read_text(encoding="utf-8")
    js = (files("clce") / "web" / "app.js").read_text(encoding="utf-8")
    css = (files("clce") / "web" / "style.css").read_text(encoding="utf-8")
    blob = html + js + css
    lowered = blob.lower()
    need = (
        "What it looks like" in html,
        "What they wrote" in html,
        "What it actually does" in html,
        "Missing pieces" in html,
        "inconsistency, not intent" in lowered,
        "cdnjs" not in lowered and "google-analytics" not in lowered and "gtag(" not in lowered,
    )
    if all(need):
        return _ok("web assets", "kid-plain labels, no CDN, no telemetry")
    return _fail("web assets", str(need))


def _check_debug() -> Check:
    # Honor the flag without requiring it to be set during doctor.
    flag = debug_enabled()
    raw = os.environ.get("CLCE_DEBUG", "")
    return _ok("CLCE_DEBUG", f"enabled={flag} raw={raw!r}")


def _check_no_telemetry() -> Check:
    src = Path(__file__).resolve().parent
    forbidden = ("google" + "-analytics", "gta" + "g(", "mix" + "panel", "sent" + "ry.io")
    hits: list[str] = []
    skip = {"doctor.py"}
    for py in src.rglob("*.py"):
        if py.name in skip:
            continue
        text = py.read_text(encoding="utf-8").lower()
        for token in forbidden:
            if token in text:
                hits.append(f"{py.name}:{token}")
    if hits:
        return _fail("no telemetry", ", ".join(hits))
    return _ok("no telemetry", "stdlib only, no analytics")


def _check_spre() -> Check:
    from spre.engine import score as spre_score
    from spre.training import NEGATIVE_CONTROLS

    official_only = spre_score(
        {
            "official": "The office says the matter is closed and the official story is complete.",
            "internal": "",
            "physics": "",
            "evidence": ["The office says the matter is closed and the official story is complete."],
        }
    )
    if "official_narrative_only" not in official_only.flags:
        return _fail("spre official-only", "missing official_narrative_only flag")
    if official_only.e > 0.25:
        return _fail("spre official-only", f"E too high ({official_only.e})")
    if official_only.asserts_guilt if hasattr(official_only, "asserts_guilt") else False:
        return _fail("spre official-only", "asserted guilt")
    blob = json.dumps(official_only.to_dict()).lower()
    if official_only.to_dict().get("asserts_guilt") or official_only.to_dict().get(
        "asserts_conspiracy"
    ):
        return _fail("spre official-only", "guilt/conspiracy asserted")
    if "not evidence" not in official_only.limitation.lower() and "not evidence" not in blob:
        return _fail("spre official-only", "limitation missing official-is-not-evidence")
    neg = spre_score(NEGATIVE_CONTROLS[0])
    if neg.ssi >= 0.35:
        return _fail("spre negative control", f"SSI too high ({neg.ssi})")
    return _ok("spre", f"E={official_only.e:.2f} neg_ssi={neg.ssi:.2f}")


def _check_transfer() -> Check:
    from clce.transfer import verify_transfer

    root = Path(__file__).resolve().parents[1]
    sample = root / "examples" / "layers.json"
    if not sample.is_file():
        return _fail("transfer", "examples/layers.json missing")
    with tempfile.TemporaryDirectory() as tmp:
        report = verify_transfer(
            path=sample,
            queue=True,
            queue_path=Path(tmp) / "q.jsonl",
            probe_central=False,
        )
    if not report.get("ok"):
        return _fail("transfer", str(report.get("error") or report.get("manifest_issues")))
    if not report.get("rescore", {}).get("clce"):
        return _fail("transfer", "CLCE rescore missing")
    return _ok("transfer", report.get("package_sha256", "")[:12] + "…")


CHECKS: tuple[Callable[[], Check], ...] = (
    _check_version,
    _check_empty,
    _check_perfect,
    _check_types,
    _check_loopback,
    _check_size_limits,
    _check_roundtrip,
    _check_web,
    _check_debug,
    _check_no_telemetry,
    _check_spre,
    _check_transfer,
)


def run_doctor() -> tuple[list[Check], bool]:
    results = [fn() for fn in CHECKS]
    passed = all(ok for _, ok, _ in results)
    return results, passed


def format_doctor(results: list[Check], passed: bool) -> str:
    lines = [f"AZ-CLCE doctor v{__version__}"]
    for name, ok, detail in results:
        mark = "ok " if ok else "FAIL"
        extra = f"  {detail}" if detail else ""
        lines.append(f"{mark}  {name}{extra}")
    lines.append("doctor: all checks passed" if passed else "doctor: FAILED")
    lines.append("CLCE detects inconsistency, not intent. Type D is a label only.")
    return "\n".join(lines) + "\n"


def doctor_payload(results: list[Check], passed: bool) -> dict:
    return {
        "ok": passed,
        "version": __version__,
        "checks": [
            {"name": name, "ok": ok, "detail": detail} for name, ok, detail in results
        ],
        "limitation": (
            "CLCE detects inconsistency, not intent. Type D is a label only."
        ),
    }
