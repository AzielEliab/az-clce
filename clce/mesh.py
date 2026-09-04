"""AzielTether extension points for AZ-CLCE and SPRE.

Prefer the central Worker when it is healthy. When it is down, score
reports wait in a local hash-chained queue. AzielTether batches consume
those items (scope ``az-clce`` or ``spre``) and reconcile to central
when the node is back online.

This is a software tether, not a VPN. It is not MirageGrid.

Author: Aziel Eliab, 2026. Apache-2.0.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from clce.engine import ENGINE_VERSION

CENTRAL_HOST = "https://azclce-download-tracker.vibelock.workers.dev"
CENTRAL_HEALTH = CENTRAL_HOST + "/v1/health"
CENTRAL_INGEST = CENTRAL_HOST + "/v1/tether-ingest"
SCOPES = frozenset({"az-clce", "spre"})
GENESIS_PREV = "0" * 64
QUEUE_ENV = "CLCE_TETHER_QUEUE"
OFFLINE_ENV = "CLCE_OFFLINE"

MESH_NOTE = (
    "AzielTether: prefer central Worker when healthy. Offline queue is "
    "hash-chained locally (scope az-clce / spre). Not a VPN. Not MirageGrid. "
    "Live public HTTPS boards stay mesh-free — the tether lives in the "
    "downloaded software."
)


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def queue_path(root: str | Path | None = None) -> Path:
    if root is not None:
        return Path(root)
    env = os.environ.get(QUEUE_ENV, "").strip()
    if env:
        return Path(env)
    return Path.home() / ".az-clce" / "tether-queue.jsonl"


def offline_forced() -> bool:
    return os.environ.get(OFFLINE_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def canonical_json(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def report_hash(report: dict) -> str:
    return sha256_hex(canonical_json(report))


def last_hash(path: Path) -> str:
    if not path.is_file():
        return GENESIS_PREV
    prev = GENESIS_PREV
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict) and item.get("hash"):
                prev = str(item["hash"])
    return prev


def make_item(report: dict, *, scope: str, prev_hash: str) -> dict:
    if scope not in SCOPES:
        raise ValueError(f"scope must be one of {sorted(SCOPES)}")
    body = {
        "created_at": utc_now(),
        "engine_version": ENGINE_VERSION,
        "prev_hash": prev_hash,
        "report_hash": report_hash(report),
        "scope": scope,
    }
    body["hash"] = sha256_hex(canonical_json(body))
    return body


def append_queue(report: dict, *, scope: str, path: Path | None = None) -> dict:
    """Append a hash-chained tether item. Offline-safe. No network."""
    dest = queue_path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    item = make_item(report, scope=scope, prev_hash=last_hash(dest))
    with dest.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(item) + "\n")
    return item


def verify_queue(path: Path | None = None) -> dict:
    dest = queue_path(path)
    if not dest.is_file():
        return {"ok": True, "items": 0, "broken": [], "note": MESH_NOTE}
    prev = GENESIS_PREV
    broken: list[str] = []
    count = 0
    with dest.open(encoding="utf-8") as handle:
        for idx, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                broken.append(f"line {idx}: invalid JSON")
                continue
            if not isinstance(item, dict):
                broken.append(f"line {idx}: not an object")
                continue
            count += 1
            expect_prev = item.get("prev_hash")
            if expect_prev != prev:
                broken.append(f"line {idx}: prev_hash mismatch")
            check = {k: v for k, v in item.items() if k != "hash"}
            if sha256_hex(canonical_json(check)) != item.get("hash"):
                broken.append(f"line {idx}: hash mismatch")
            prev = str(item.get("hash") or prev)
    return {
        "ok": not broken,
        "items": count,
        "broken": broken,
        "tip_hash": prev if count else GENESIS_PREV,
        "note": MESH_NOTE,
    }


def central_healthy(*, timeout: float = 2.0) -> dict:
    """Probe the central Worker. Offline-forced or errors → unhealthy."""
    if offline_forced():
        return {
            "ok": False,
            "reason": "CLCE_OFFLINE",
            "prefer_central": False,
            "note": MESH_NOTE,
        }
    req = Request(CENTRAL_HEALTH, headers={"User-Agent": "Mozilla/5.0 AZ-CLCE"})
    try:
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310 — public health URL
            body = json.loads(resp.read().decode("utf-8"))
        ok = bool(body.get("ok"))
        return {
            "ok": ok,
            "reason": "healthy" if ok else "unhealthy",
            "prefer_central": ok,
            "version": body.get("version"),
            "note": MESH_NOTE,
        }
    except (URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "reason": str(exc),
            "prefer_central": False,
            "note": MESH_NOTE,
        }


def prefer_central(health: dict | None = None) -> bool:
    if health is None:
        return False
    return bool(health.get("ok") and health.get("prefer_central"))


def enqueue_or_note(
    report: dict,
    *,
    scope: str,
    path: Path | None = None,
    probe: bool = False,
) -> dict:
    """Always persist locally. Optionally note whether central is preferred.

    Network is never required. ``probe=True`` may try /v1/health.
    """
    item = append_queue(report, scope=scope, path=path)
    health = central_healthy() if probe and not offline_forced() else {
        "ok": False,
        "reason": "not_probed",
        "prefer_central": False,
        "note": MESH_NOTE,
    }
    return {
        "queued": item,
        "central": health,
        "ingest_hint": CENTRAL_INGEST,
        "note": MESH_NOTE,
        "vpn": False,
        "miragegrid": False,
    }


def mesh_status(path: Path | None = None, *, probe: bool = False) -> dict:
    return {
        "author": "Aziel Eliab",
        "central_health": CENTRAL_HEALTH,
        "central_ingest": CENTRAL_INGEST,
        "scopes": sorted(SCOPES),
        "queue": str(queue_path(path)),
        "queue_verify": verify_queue(path),
        "central": central_healthy() if probe else {"ok": None, "reason": "not_probed"},
        "offline_forced": offline_forced(),
        "note": MESH_NOTE,
        "vpn": False,
        "miragegrid": False,
    }
