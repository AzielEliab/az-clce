"""Aziel triad: SPRE + CLCE + PhysLing component scores.

SPRE and CLCE live here. PhysLing lives in aziel-corpus. This module
exposes a stable JSON slot so corpus can form **one combined final
score** when all three have verified.

Canonical unit is the closed interval [0, 1]. Each component also
emits ``score_100`` (0–100) for display. Higher ``score`` = stronger
verification / cleaner for compositing.

    clce.score  = triple
    spre.score  = 1 − PC     (PC is suppression-pattern confidence, not guilt)
    physling    = filled by aziel-corpus

    final.score = mean(spre, clce, physling)  iff all three verified
    otherwise final.score is null and ready is false.

Author: Aziel Eliab, 2026. Apache-2.0.
"""

from __future__ import annotations

import json
from typing import Iterable

SCHEMA_TRIAD = "aziel.triad.v0.3"
SCHEMA_COMPONENT = "aziel.triad.component.v0.3"
VERIFIERS = ("spre", "clce", "physling")
PHYSLING_HOME = "aziel-corpus"
CLCE_HOME = "az-clce"
SPRE_HOME = "az-clce"

UNIT = "unit_interval"
UNIT_100 = "percent_0_100"
POLARITY = "higher_is_stronger_verification"
COMBINE_WHEN = "all_three_verified"
FORMULA = (
    "final.score = (spre.score + clce.score + physling.score) / 3 "
    "when spre.verified and clce.verified and physling.verified; "
    "else final.score is null"
)

LIMITATION = (
    "Triad components are advisory. CLCE detects inconsistency, not intent. "
    "Type D is a label, not malice. SPRE never asserts guilt. PhysLing lives "
    "in aziel-corpus. Official narrative is not evidence. Author: Aziel Eliab."
)


def clip01(value: float | None) -> float | None:
    if value is None:
        return None
    number = float(value)
    if number < 0.0:
        return 0.0
    if number > 1.0:
        return 1.0
    return number


def score_100(value: float | None) -> float | None:
    unit = clip01(value)
    if unit is None:
        return None
    return round(unit * 100.0, 4)


def _base(id_: str, home: str, *, verified: bool, score: float | None, note: str, raw: dict | None = None) -> dict:
    unit = clip01(score) if verified and score is not None else None
    return {
        "schema": SCHEMA_COMPONENT,
        "id": id_,
        "home": home,
        "verified": bool(verified and unit is not None),
        "score": unit,
        "score_100": score_100(unit),
        "unit": UNIT,
        "unit_100": UNIT_100,
        "polarity": POLARITY,
        "raw": raw or {},
        "note": note,
    }


def unverified(id_: str) -> dict:
    homes = {"spre": SPRE_HOME, "clce": CLCE_HOME, "physling": PHYSLING_HOME}
    notes = {
        "spre": "SPRE has not verified this payload.",
        "clce": "CLCE has not verified this payload.",
        "physling": (
            "PhysLing lives in aziel-corpus. Empty slot for corpus merge."
        ),
    }
    return _base(id_, homes.get(id_, CLCE_HOME), verified=False, score=None, note=notes.get(id_, ""))


def physling_slot() -> dict:
    return unverified("physling")


def clce_component(
    triple: float,
    *,
    plus: float | None = None,
    pairwise_avg: float | None = None,
    band: str | None = None,
) -> dict:
    return _base(
        "clce",
        CLCE_HOME,
        verified=True,
        score=float(triple),
        raw={"triple": triple, "plus": plus, "pairwise_avg": pairwise_avg, "band": band},
        note=(
            "CLCE triple on [0, 1]. Higher = more cross-layer consistency. "
            "Type D is a label, not malice."
        ),
    )


def spre_component(
    pc: float,
    *,
    ssi: float | None = None,
    e: float | None = None,
    flags: Iterable[str] | None = None,
) -> dict:
    integrity = 1.0 - float(pc)
    return _base(
        "spre",
        SPRE_HOME,
        verified=True,
        score=integrity,
        raw={
            "pc": pc,
            "ssi": ssi,
            "e": e,
            "flags": list(flags or ()),
            "pc_is_suppression_confidence": True,
            "merge_score": "1 - pc",
        },
        note=(
            "Merge score is 1−PC on [0, 1]. Raw PC is suppression-pattern "
            "confidence (structural similarity × evidence). Not guilt."
        ),
    )


def assemble(
    *,
    clce: dict | None = None,
    spre: dict | None = None,
    physling: dict | None = None,
) -> dict:
    components = {
        "spre": spre if spre and spre.get("id") == "spre" else unverified("spre"),
        "clce": clce if clce and clce.get("id") == "clce" else unverified("clce"),
        "physling": physling if physling and physling.get("id") == "physling" else physling_slot(),
    }
    verified = [
        key
        for key in VERIFIERS
        if components[key].get("verified") and components[key].get("score") is not None
    ]
    ready = verified == list(VERIFIERS)
    final_score = None
    if ready:
        final_score = sum(float(components[key]["score"]) for key in VERIFIERS) / 3.0
        final_score = clip01(final_score)
    return {
        "schema": SCHEMA_TRIAD,
        "author": "Aziel Eliab",
        "verifiers": list(VERIFIERS),
        "physling_home": PHYSLING_HOME,
        "combine_when": COMBINE_WHEN,
        "unit": UNIT,
        "unit_100": UNIT_100,
        "polarity": POLARITY,
        "formula": FORMULA,
        "components": components,
        "final": {
            "score": final_score,
            "score_100": score_100(final_score),
            "verified_count": len(verified),
            "verified": verified,
            "ready": ready,
            "note": (
                "aziel-corpus / PhysLing fills the physling slot. Combined "
                "final is computed only when all three have verified."
            ),
        },
        "limitation": LIMITATION,
        "advisory": True,
        "asserts_guilt": False,
    }


def mean_component(id_: str, parts: list[dict]) -> dict | None:
    ok = [p for p in parts if p and p.get("verified") and p.get("score") is not None]
    if not ok:
        return None
    avg = sum(float(p["score"]) for p in ok) / len(ok)
    if id_ == "clce":
        triples = [p.get("raw", {}).get("triple") for p in ok]
        triples = [t for t in triples if t is not None]
        triple = sum(triples) / len(triples) if triples else avg
        return clce_component(triple)
    if id_ == "spre":
        pcs = [p.get("raw", {}).get("pc") for p in ok]
        pcs = [x for x in pcs if x is not None]
        pc = sum(pcs) / len(pcs) if pcs else (1.0 - avg)
        return spre_component(pc)
    return None


def clce_from_mapping(obj: dict) -> dict | None:
    """Build a CLCE component from a live report or an older stored payload."""
    if not isinstance(obj, dict):
        return None
    if obj.get("triple") is not None:
        pairwise = obj.get("pairwise") if isinstance(obj.get("pairwise"), dict) else {}
        avg = obj.get("pairwise_avg")
        if avg is None and pairwise:
            vals = [pairwise.get(k) for k in ("rd", "dp", "rp") if pairwise.get(k) is not None]
            avg = sum(vals) / len(vals) if vals else None
        return clce_component(
            float(obj["triple"]),
            plus=obj.get("plus"),
            pairwise_avg=avg,
            band=obj.get("band"),
        )
    return None


def spre_from_mapping(obj: dict) -> dict | None:
    """Build a SPRE component from a live report or an older stored payload."""
    if not isinstance(obj, dict):
        return None
    pc = obj.get("pc")
    if pc is None and isinstance(obj.get("sp"), dict) and obj["sp"].get("e") is not None:
        ssi = obj.get("ssi")
        if ssi is not None:
            pc = float(ssi) * float(obj["sp"]["e"])
    if pc is None:
        return None
    sp = obj.get("sp") if isinstance(obj.get("sp"), dict) else {}
    return spre_component(
        float(pc),
        ssi=obj.get("ssi"),
        e=sp.get("e"),
        flags=obj.get("flags") or (),
    )


def triad_from_reports(*, clce: dict | None = None, spre: dict | None = None) -> dict:
    return assemble(
        clce=clce_from_mapping(clce) if clce else None,
        spre=spre_from_mapping(spre) if spre else None,
    )


def looks_clce_report(obj: dict) -> bool:
    schema = str(obj.get("schema") or "")
    return schema.startswith("az-clce.report.") or obj.get("triple") is not None


def looks_spre_report(obj: dict) -> bool:
    schema = str(obj.get("schema") or "")
    return schema.startswith("spre.report.") or obj.get("pc") is not None or obj.get("ssi") is not None


def schema_doc() -> dict:
    """Machine-readable compositing contract for aziel-corpus."""
    return {
        "schema": SCHEMA_TRIAD,
        "author": "Aziel Eliab",
        "verifiers": list(VERIFIERS),
        "physling_home": PHYSLING_HOME,
        "unit": UNIT,
        "range": {"min": 0.0, "max": 1.0},
        "unit_100": UNIT_100,
        "range_100": {"min": 0.0, "max": 100.0},
        "polarity": POLARITY,
        "combine_when": COMBINE_WHEN,
        "formula": FORMULA,
        "fields": {
            "components.spre.score": "1 − PC (0–1). PC = SSI × E.",
            "components.clce.score": "Jaccard triple (0–1).",
            "components.physling.score": "Filled by aziel-corpus PhysLing (0–1).",
            "final.score": "Mean of the three scores when all verified; else null.",
            "score_100": "score × 100 (display twin).",
        },
        "limitation": LIMITATION,
    }


def dumps(obj: dict) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)
