"""Import layers {r,d,p,n} from JSON/txt and export report JSON + receipt.

Empty fields are OK. Size limits are enforced via engine.check_field.
SHA-256 covers the canonical JSON of the four inputs only.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from clce.engine import (
    ENGINE_VERSION,
    LIMITATION,
    MAX_BODY_BYTES,
    MAX_FIELD_CHARS,
    TYPE_LABELS,
    Report,
    check_field,
    debug,
)

SCHEMA_REPORT = "az-clce.report.v0.2"
SCHEMA_RECEIPT = "az-clce.receipt.v0.2"

_LAYER_ALIASES = {
    "r": "r",
    "representation": "r",
    "what it looks like": "r",
    "what it looks like (r)": "r",
    "looks like": "r",
    "d": "d",
    "description": "d",
    "what they wrote": "d",
    "what they wrote (d)": "d",
    "they wrote": "d",
    "p": "p",
    "reality": "p",
    "what it actually does": "p",
    "what it actually does (p)": "p",
    "actually does": "p",
    "n": "n",
    "missing": "n",
    "missing pieces": "n",
    "missing pieces (n)": "n",
    "negative": "n",
    "negative space": "n",
    "negative_space": "n",
}

_STOP_HEADERS = frozenset(
    {
        "score",
        "band",
        "kid-plain",
        "kid plain",
        "jaccard",
        "types",
        "primary",
        "limitation",
        "input_sha256",
        "input sha256",
        "sha256",
        "version",
        "schema",
        "generated",
        "az-clce receipt",
        "pairwise",
        "pairwise avg",
        "pairwise average",
        "clce+",
        "triple",
        "advisory",
        "threshold",
        "r↔d",
        "d↔p",
        "r↔p",
    }
)

_HEADER_LINE = re.compile(r"^(.{1,80}?)\s*:\s*(.*)$")


class LayerImportError(ValueError):
    """Layer import failed. Name avoids colliding with builtins.ImportError."""


def _norm_header(raw: str) -> str:
    s = raw.strip().lower()
    s = s.replace("—", "-").replace("–", "-")
    s = re.sub(r"\s+", " ", s)
    return s


def _as_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(str(v) for v in value if v is not None)
    return str(value)


def _layers_from_mapping(obj: dict) -> dict[str, str]:
    def pick(*keys: str) -> str:
        for key in keys:
            if key in obj and obj[key] is not None:
                return _as_text(obj[key])
        layers = obj.get("layers")
        if isinstance(layers, dict):
            for key in keys:
                if key in layers and layers[key] is not None:
                    return _as_text(layers[key])
        return ""

    out = {
        "r": pick("r", "R", "representation"),
        "d": pick("d", "D", "description"),
        "p": pick("p", "P", "reality"),
        "n": pick("n", "N", "negative", "negative_space", "missing"),
    }
    return {
        "r": check_field("r", out["r"]),
        "d": check_field("d", out["d"]),
        "p": check_field("p", out["p"]),
        "n": check_field("n", out["n"]),
    }


def _parse_labeled(text: str) -> dict[str, str]:
    buckets: dict[str, list[str]] = {"r": [], "d": [], "p": [], "n": []}
    current: str | None = None
    for raw_line in text.splitlines():
        match = _HEADER_LINE.match(raw_line.strip())
        if match:
            header = _norm_header(match.group(1))
            rest = match.group(2)
            if header in _LAYER_ALIASES:
                current = _LAYER_ALIASES[header]
                if rest:
                    buckets[current].append(rest)
                continue
            if header in _STOP_HEADERS or header.startswith("type "):
                current = None
                continue
        if current is not None:
            buckets[current].append(raw_line.rstrip())
    def _clean(value: str) -> str:
        text = value.strip()
        if text.lower() == "(empty)":
            return ""
        return text

    out = {k: _clean("\n".join(v)) for k, v in buckets.items()}
    return {
        "r": check_field("r", out["r"]),
        "d": check_field("d", out["d"]),
        "p": check_field("p", out["p"]),
        "n": check_field("n", out["n"]),
    }


def parse_layers(text: str) -> dict[str, str]:
    """Parse JSON or labeled text into {r,d,p,n}. Empty fields OK."""
    if text is None:
        raise LayerImportError("empty import")
    if len(text.encode("utf-8")) > MAX_BODY_BYTES:
        raise LayerImportError(f"import exceeds size limit ({MAX_BODY_BYTES} bytes)")
    blob = text.lstrip("\ufeff").strip()
    if not blob:
        return {"r": "", "d": "", "p": "", "n": ""}
    if blob[0] in "{[":
        try:
            obj = json.loads(blob)
        except json.JSONDecodeError as exc:
            raise LayerImportError(f"invalid JSON: {exc}") from exc
        if isinstance(obj, dict):
            layers = _layers_from_mapping(obj)
            debug(f"import json layers r={len(layers['r'])} d={len(layers['d'])} p={len(layers['p'])} n={len(layers['n'])}")
            return layers
        raise LayerImportError("JSON object required")
    layers = _parse_labeled(blob)
    debug(f"import txt layers r={len(layers['r'])} d={len(layers['d'])} p={len(layers['p'])} n={len(layers['n'])}")
    return layers


def load_layers(path: str | Path) -> dict[str, str]:
    raw = Path(path).read_bytes()
    if len(raw) > MAX_BODY_BYTES:
        raise LayerImportError(f"import exceeds size limit ({MAX_BODY_BYTES} bytes)")
    return parse_layers(raw.decode("utf-8"))


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def receipt_text(report: Report, *, generated: str | None = None) -> str:
    """Human-readable .txt receipt with sha256 of inputs."""
    stamp = generated or utc_now()
    n_body = report.n if report.n.strip() else "(empty)"
    if report.types:
        types_line = ", ".join(f"{c} {TYPE_LABELS[c]}" for c in report.types)
        primary_line = f"{report.primary} {TYPE_LABELS[report.primary]}" if report.primary else "(none)"
    else:
        types_line = "(none)"
        primary_line = "(none)"
    return "\n".join(
        [
            "AZ-CLCE receipt",
            "===============",
            f"version: {report.version}",
            f"schema: {SCHEMA_RECEIPT}",
            f"generated: {stamp}",
            "",
            LIMITATION,
            "",
            "input_sha256 (canonical JSON of {d,n,p,r}, sort_keys, UTF-8):",
            f"  {report.input_sha256}",
            "",
            "What it looks like (R):",
            f"  {report.r if report.r.strip() else '(empty)'}",
            "",
            "What they wrote (D):",
            f"  {report.d if report.d.strip() else '(empty)'}",
            "",
            "What it actually does (P):",
            f"  {report.p if report.p.strip() else '(empty)'}",
            "",
            "Missing pieces (N):",
            f"  {n_body}",
            "",
            f"Score: {report.triple:.4f}",
            f"Band: {report.band}",
            "Kid-plain:",
            f"  {report.kid_plain}",
            "",
            "Jaccard:",
            f"  R↔D  {report.pairwise_rd:.4f}",
            f"  D↔P  {report.pairwise_dp:.4f}",
            f"  R↔P  {report.pairwise_rp:.4f}",
            f"  pairwise average  {report.pairwise_avg:.4f}",
            f"  CLCE+  {report.plus:.4f}",
            "",
            f"Types: {types_line}",
            f"Primary: {primary_line}",
            "",
            "Limitation:",
            f"  {report.limitation}",
            "",
            "CLCE detects inconsistency, not intent. Type D is a label only.",
            "Not a scanner. Not a lie detector. Advisory scores only.",
            "",
        ]
    )


def report_json_text(report: Report) -> str:
    payload = report.to_dict()
    payload["schema"] = SCHEMA_REPORT
    payload["version"] = report.version or ENGINE_VERSION
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def export_paths(path: str | Path) -> tuple[Path, Path]:
    """Return (json_path, txt_path) next to the given export path."""
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".txt":
        return p.with_suffix(".json"), p
    if suffix == ".json":
        return p, p.with_suffix(".txt")
    if suffix:
        return p.with_suffix(".json"), p.with_suffix(".txt")
    return Path(str(p) + ".json"), Path(str(p) + ".txt")


def write_export(path: str | Path, report: Report) -> tuple[Path, Path]:
    json_path, txt_path = export_paths(path)
    json_path.write_text(report_json_text(report), encoding="utf-8")
    txt_path.write_text(receipt_text(report), encoding="utf-8")
    debug(f"export json={json_path} txt={txt_path} sha256={report.input_sha256}")
    return json_path, txt_path


# Re-export limits so CLI/UI import from one place.
__all__ = [
    "LayerImportError",
    "MAX_BODY_BYTES",
    "MAX_FIELD_CHARS",
    "SCHEMA_RECEIPT",
    "SCHEMA_REPORT",
    "export_paths",
    "load_layers",
    "parse_layers",
    "receipt_text",
    "report_json_text",
    "utc_now",
    "write_export",
]
