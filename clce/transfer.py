"""Transfer verify + rescore for AZ-CLCE and SPRE.

On any sensed upload or download (local CLI or Worker ingest hook):
verify the structure of every file, re-run SPRE + CLCE, rescore, and
emit a machine-readable JSON report.

Author: Aziel Eliab, 2026. Apache-2.0.
"""

from __future__ import annotations

import hashlib
import json
import tarfile
from pathlib import Path

from clce.engine import (
    ENGINE_VERSION,
    LIMITATION as CLCE_LIMITATION,
    MAX_BODY_BYTES,
    MAX_FIELD_CHARS,
    score as clce_score,
)
from clce.io import LayerImportError, parse_layers
from clce.mesh import MESH_NOTE, enqueue_or_note, report_hash
from clce.triad import (
    assemble,
    clce_from_mapping,
    looks_clce_report,
    looks_spre_report,
    mean_component,
    schema_doc,
    spre_from_mapping,
    triad_from_reports,
)

SCHEMA_TRANSFER = "az-clce.transfer.v0.3"
SCHEMA_PACKAGE = "az-clce.transfer-package.v0.3"
MAX_FILES = 256
MAX_FILES_BACKFILL = 2048
SKIP_DIR_NAMES = frozenset(
    {".git", ".venv", "__pycache__", "node_modules", ".pytest_cache", ".wrangler"}
)
TEXT_SUFFIXES = frozenset(
    {".json", ".txt", ".md", ".csv", ".py", ".js", ".toml", ".yml", ".yaml", ".html"}
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _kind_for(name: str, data: bytes) -> str:
    lower = name.lower()
    if lower.endswith(".tar.gz") or lower.endswith(".tgz"):
        return "tar.gz"
    if lower.endswith(".json"):
        return "json"
    if not data:
        return "empty"
    if data[:1] in (b"{", b"["):
        return "json"
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return "binary"
    return "text"


def _looks_spre(obj: dict) -> bool:
    keys = {k.lower() for k in obj}
    spre_keys = {
        "official",
        "official_narrative",
        "internal",
        "physics",
        "coroner",
        "authority",
        "victim_framing",
        "destroyed",
        "records",
    }
    return bool(keys & spre_keys) or looks_spre_report(obj) or str(obj.get("schema") or "").startswith("spre.")


def _looks_clce(obj: dict) -> bool:
    keys = {k.lower() for k in obj}
    return bool(keys & {"r", "d", "p", "n", "representation", "description", "reality"}) or looks_clce_report(obj)


def _looks_package(obj: dict) -> bool:
    return obj.get("schema") == SCHEMA_PACKAGE or (
        isinstance(obj.get("files"), list) and "package" in str(obj.get("schema", "")).lower()
    )


def verify_bytes(name: str, data: bytes) -> dict:
    """Structure check for one file's bytes."""
    issues: list[str] = []
    size = len(data)
    if size > MAX_BODY_BYTES:
        issues.append(f"exceeds size limit ({size} > {MAX_BODY_BYTES})")
    kind = _kind_for(name, data)
    parse_ok = True
    parsed: object = None
    if kind == "json":
        try:
            parsed = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            parse_ok = False
            issues.append(f"invalid JSON: {exc}")
    elif kind == "text":
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as exc:
            parse_ok = False
            issues.append(f"invalid UTF-8: {exc}")
    elif kind == "tar.gz":
        try:
            import io

            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
                members = archive.getmembers()
            parsed = {"members": len(members)}
        except (tarfile.TarError, OSError) as exc:
            parse_ok = False
            issues.append(f"invalid tar.gz: {exc}")
    elif kind == "empty":
        issues.append("empty file")
    return {
        "name": name,
        "size": size,
        "sha256": _sha256_bytes(data),
        "kind": kind,
        "parse_ok": parse_ok,
        "issues": issues,
        "ok": parse_ok and not any("exceeds" in i for i in issues),
        "parsed_type": type(parsed).__name__ if parsed is not None else None,
    }


def _rescore_payload(name: str, data: bytes, structure: dict) -> dict:
    from spre.engine import LIMITATION as SPRE_LIMITATION
    from spre.engine import score as spre_score
    from spre.engine import score_from_text

    clce_out = None
    spre_out = None
    notes: list[str] = []
    if not structure.get("ok"):
        return {
            "clce": None,
            "spre": None,
            "notes": structure.get("issues") or ["structure failed; skipped rescore"],
        }
    kind = structure.get("kind")
    if kind == "binary":
        notes.append("binary: structure-only; no semantic SPRE/CLCE rescore")
        return {"clce": None, "spre": None, "notes": notes}
    if kind == "tar.gz":
        notes.append("archive: members verified separately when unpacked")
        return {"clce": None, "spre": None, "notes": notes}
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        notes.append("not UTF-8; structure-only")
        return {"clce": None, "spre": None, "notes": notes}
    if kind == "json" or text.lstrip()[:1] in "{[":
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            obj = None
        if isinstance(obj, dict):
            if _looks_clce(obj):
                try:
                    layers = parse_layers(text)
                    if any(layers.values()):
                        clce_out = clce_score(**layers).to_dict()
                    elif looks_clce_report(obj):
                        clce_out = dict(obj)
                        notes.append("CLCE backfill from stored report (older payload)")
                except (LayerImportError, ValueError) as exc:
                    if looks_clce_report(obj):
                        clce_out = dict(obj)
                        notes.append(f"CLCE backfill from stored report: {exc}")
                    else:
                        notes.append(f"CLCE rescore skipped: {exc}")
            if _looks_spre(obj):
                try:
                    if looks_spre_report(obj) and not any(
                        obj.get(k) for k in ("official", "official_narrative", "internal", "physics")
                    ):
                        spre_out = dict(obj)
                        notes.append("SPRE backfill from stored report (older payload)")
                    else:
                        spre_out = spre_score(obj).to_dict()
                except ValueError as exc:
                    if looks_spre_report(obj):
                        spre_out = dict(obj)
                        notes.append(f"SPRE backfill from stored report: {exc}")
                    else:
                        notes.append(f"SPRE rescore skipped: {exc}")
            if clce_out is None and spre_out is None:
                # Unknown JSON: conservative SPRE on dumped text, no CLCE guess.
                spre_out = score_from_text(text[:MAX_FIELD_CHARS]).to_dict()
                notes.append("unlabeled JSON: SPRE notes-only (anti-apophenia)")
        else:
            notes.append("JSON value is not an object")
    else:
        try:
            layers = parse_layers(text)
            if any(layers.values()):
                clce_out = clce_score(**layers).to_dict()
        except (LayerImportError, ValueError):
            pass
        spre_out = score_from_text(text[:MAX_FIELD_CHARS]).to_dict()
        notes.append("text: SPRE notes-only unless labeled layers parsed")
    if clce_out is not None:
        notes.append(CLCE_LIMITATION)
    if spre_out is not None:
        notes.append(SPRE_LIMITATION)
    return {"clce": clce_out, "spre": spre_out, "notes": notes}


def _iter_dir(root: Path, *, limit: int = MAX_FILES) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        files.append(path)
        if len(files) >= limit:
            break
    return files


def _collect(path: Path, *, limit: int = MAX_FILES) -> list[tuple[str, bytes]]:
    if path.is_file() and (
        path.name.endswith(".tar.gz") or path.name.endswith(".tgz")
    ):
        out: list[tuple[str, bytes]] = []
        with tarfile.open(path, mode="r:gz") as archive:
            for member in archive.getmembers():
                if not member.isfile():
                    continue
                extracted = archive.extractfile(member)
                if extracted is None:
                    continue
                data = extracted.read()
                out.append((member.name, data))
                if len(out) >= limit:
                    break
        return out
    if path.is_file():
        return [(path.name, path.read_bytes())]
    if path.is_dir():
        return [(str(p.relative_to(path)), p.read_bytes()) for p in _iter_dir(path, limit=limit)]
    raise FileNotFoundError(path)


def _manifest_issues(files: list[dict], package_obj: dict | None) -> list[str]:
    if not package_obj or not isinstance(package_obj.get("files"), list):
        return []
    issues: list[str] = []
    have = {f["name"]: f for f in files}
    for entry in package_obj["files"]:
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("path") or entry.get("name") or "")
        expect = entry.get("sha256")
        if not name or not expect:
            continue
        got = have.get(name)
        if got is None:
            issues.append(f"manifest missing file: {name}")
        elif got["sha256"] != expect:
            issues.append(f"manifest hash mismatch: {name}")
    return issues


def _row_triad(rescore: dict) -> dict:
    return triad_from_reports(clce=rescore.get("clce"), spre=rescore.get("spre"))


def verify_transfer(
    path: str | Path | None = None,
    *,
    files: list[dict] | None = None,
    direction: str = "local",
    queue: bool = True,
    queue_path: Path | None = None,
    probe_central: bool = False,
    backfill: bool = False,
) -> dict:
    """Verify a path, an in-memory file list, or a Worker ingest body."""
    file_rows: list[dict] = []
    package_obj = None
    collection_error = None
    blobs: list[tuple[str, bytes]] = []
    file_limit = MAX_FILES_BACKFILL if backfill else MAX_FILES
    if files is not None:
        for item in files[:file_limit]:
            name = str(item.get("name") or item.get("path") or "unnamed")
            if item.get("text") is not None:
                data = str(item.get("text")).encode("utf-8")
            elif item.get("b64"):
                import base64

                data = base64.b64decode(item["b64"])
            else:
                data = b""
            blobs.append((name, data))
    elif path is not None:
        try:
            blobs = _collect(Path(path), limit=file_limit)
        except (OSError, tarfile.TarError) as exc:
            collection_error = str(exc)
    else:
        collection_error = "PATH or files required"

    if collection_error:
        payload = {
            "schema": SCHEMA_TRANSFER,
            "version": ENGINE_VERSION,
            "author": "Aziel Eliab",
            "direction": direction,
            "ok": False,
            "error": collection_error,
            "files": [],
            "limitation": CLCE_LIMITATION,
            "mesh": MESH_NOTE,
        }
        return payload

    for name, data in blobs:
        structure = verify_bytes(name, data)
        rescore = _rescore_payload(name, data, structure)
        row = {**structure, "rescore": rescore, "triad": _row_triad(rescore)}
        file_rows.append(row)
        if structure.get("kind") == "json" and data:
            try:
                obj = json.loads(data.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                obj = None
            if isinstance(obj, dict) and _looks_package(obj):
                package_obj = obj

    manifest_issues = _manifest_issues(file_rows, package_obj)
    structure_ok = all(row.get("ok") for row in file_rows) and not manifest_issues
    if not file_rows:
        structure_ok = False
        manifest_issues.append("empty transfer package")

    clce_scores = [r["rescore"]["clce"] for r in file_rows if r["rescore"].get("clce")]
    spre_scores = [r["rescore"]["spre"] for r in file_rows if r["rescore"].get("spre")]
    clce_parts = [clce_from_mapping(s) for s in clce_scores]
    spre_parts = [spre_from_mapping(s) for s in spre_scores]
    triad = assemble(
        clce=mean_component("clce", [p for p in clce_parts if p]),
        spre=mean_component("spre", [p for p in spre_parts if p]),
    )
    package_sha = _sha256_bytes(
        "".join(sorted(r["sha256"] for r in file_rows)).encode("utf-8")
    )
    report = {
        "schema": SCHEMA_TRANSFER,
        "version": ENGINE_VERSION,
        "author": "Aziel Eliab",
        "direction": direction,
        "ok": structure_ok,
        "backfill": backfill,
        "file_count": len(file_rows),
        "package_sha256": package_sha,
        "files": file_rows,
        "manifest_issues": manifest_issues,
        "triad": triad,
        "triad_schema": schema_doc(),
        "rescore": {
            "clce_count": len(clce_scores),
            "spre_count": len(spre_scores),
            "clce": clce_scores[0] if len(clce_scores) == 1 else clce_scores,
            "spre": spre_scores[0] if len(spre_scores) == 1 else spre_scores,
        },
        "limitation": (
            "Transfer verify checks structure and re-scores. CLCE detects "
            "inconsistency, not intent. Type D is a label, not malice. "
            "SPRE never asserts guilt or conspiracy. Official narrative "
            "is not evidence."
        ),
        "mesh": MESH_NOTE,
        "advisory": True,
        "asserts_guilt": False,
    }
    if queue:
        mesh = enqueue_or_note(
            report,
            scope="az-clce",
            path=queue_path,
            probe=probe_central,
        )
        # Also chain a spre-scoped item when any SPRE rescore ran.
        if spre_scores:
            mesh["spre"] = enqueue_or_note(
                report,
                scope="spre",
                path=queue_path,
                probe=False,
            )
        report["tether"] = {
            "queued": True,
            "item": mesh.get("queued"),
            "central": mesh.get("central"),
            "note": MESH_NOTE,
            "report_hash": report_hash(report),
        }
    else:
        report["tether"] = {"queued": False, "note": MESH_NOTE}
    return report


def verify_transfer_path(path: str | Path, **kwargs) -> dict:
    return verify_transfer(path=path, **kwargs)


def file_records(report: dict) -> list[dict]:
    """One triad-bearing record per file for corpus backfill / NDJSON."""
    out: list[dict] = []
    for row in report.get("files") or []:
        rescore = row.get("rescore") or {}
        out.append(
            {
                "schema": "aziel.triad.record.v0.3",
                "author": "Aziel Eliab",
                "name": row.get("name"),
                "sha256": row.get("sha256"),
                "ok": row.get("ok"),
                "triad": row.get("triad") or _row_triad(rescore),
                "clce": rescore.get("clce"),
                "spre": rescore.get("spre"),
                "physling": None,
                "asserts_guilt": False,
            }
        )
    return out


def backfill_path(path: str | Path, **kwargs) -> dict:
    """Score a directory (or archive) of older payloads for triad merge."""
    return verify_transfer(path=path, backfill=True, **kwargs)
