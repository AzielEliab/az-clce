"""Structural Suppression Pattern Recognition Engine (SPRE).

SP(c) = {P1..P5, E, C, T, D}

P1 Two-Story Narrative (official vs internal/physics contradiction).
   Official-narrative-only is itself a flagged pattern.
P2 Coroner–Authority Loop
P3 Evidence Destruction
P4 Victim-Blame Inversion
P5 Paper-Trail Erasure

E  evidence independence — official narrative is NEVER evidence
C  coverage of independent source kinds
T  temporal contemporaneity
D  documentation completeness (not CLCE Type D)

SSI  structural similarity to the training set
PC   pattern confidence = SSI × E

Training set = historically confirmed failures only.
Testing = structural similarity. NEVER assert guilt or conspiracy.

Author: Aziel Eliab, 2026. Apache-2.0.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Iterable

from clce.engine import MAX_FIELD_CHARS, check_field, jaccard, tokenize

from spre.training import TRAINING_CASES

ENGINE_VERSION = "0.3.0"
SCHEMA_REPORT = "spre.report.v0.3"
SCHEMA_CASE = "spre.case.v0.3"

# Anti-apophenia: a near-zero pattern vector is not similar to anything.
MIN_VECTOR_NORM = 0.15
# At least two cues above this line before SSI is trusted.
CUE_FLOOR = 0.40
MIN_CUES = 2
# Short text cannot support a pattern claim.
MIN_TOKENS_FOR_SSI = 24
WEAK_CUE_SUM = 0.80

LIMITATION = (
    "SPRE scores structural similarity to historically confirmed failures. "
    "It never asserts guilt, conspiracy, or intent. Official narrative is "
    "not evidence. Official narrative without independent evidence or "
    "physics lowers E and raises poison-suspicion flags. Human validation "
    "required. Advisory only. Not a court, not a lie detector, not CLCE "
    "Type D (CLCE Type D remains a label, not malice)."
)

P_LABELS = {
    "p1": "Two-Story Narrative",
    "p2": "Coroner–Authority Loop",
    "p3": "Evidence Destruction",
    "p4": "Victim-Blame Inversion",
    "p5": "Paper-Trail Erasure",
}

P_NOTES = {
    "p1": (
        "Official story versus internal or physical story. If only the "
        "official story is present, that absence is itself a pattern — "
        "not proof of a second story."
    ),
    "p2": (
        "The office that certifies medical or forensic facts is the same "
        "office that investigates. Circular certification, not a motive."
    ),
    "p3": (
        "Material that should exist is listed as destroyed, lost, wiped, "
        "or never collected. A list of gaps, not a charge."
    ),
    "p4": (
        "The harmed party is framed as the cause without independent "
        "support. Framing pattern, not a finding about the person."
    ),
    "p5": (
        "Logs, chain of custody, or contemporaneous records are missing "
        "or described as shredded, unlogged, or broken."
    ),
}

DESTROY_TOKENS = frozenset(
    {
        "destroyed",
        "incinerated",
        "overwritten",
        "discarded",
        "wiped",
        "shredded",
        "deleted",
        "unexamined",
        "burned",
        "lost",
        "missing",
    }
)
DESTROY_PHRASES = (
    "never collected",
    "never filed",
    "tape missing",
    "files burned",
    "evidence lost",
    "body missing",
)

BLAME_TOKENS = frozenset(
    {
        "reckless",
        "crazy",
        "suicide",
        "deserved",
        "noncompliant",
        "resisted",
        "lifestyle",
        "hysterical",
        "uncooperative",
        "junkie",
        "drunk",
        "fault",
        "blamed",
    }
)
BLAME_PHRASES = (
    "brought it on",
    "brought this on",
    "their own fault",
    "asked for it",
)

ERASURE_TOKENS = frozenset(
    {
        "unlogged",
        "shredded",
        "unfiled",
        "redacted",
        "gap",
        "gaps",
        "neverfiled",
    }
)
ERASURE_PHRASES = (
    "no log",
    "no record",
    "never filed",
    "pages missing",
    "destroyed logs",
    "broken chain",
    "chain of custody broken",
    "custody was broken",
    "custody broken",
)

LOOP_TOKENS = frozenset(
    {
        "inhouse",
        "in-house",
        "attached",
        "same",
        "department",
    }
)
LOOP_PHRASES = (
    "same office",
    "same authority",
    "employed by",
    "in-house",
    "police coroner",
    "department coroner",
)

AFTER_FACT_PHRASES = (
    "years later",
    "after the fact",
    "later reconstructed",
    "from memory",
    "reconstructed later",
)


def _clip(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


def _has_phrase(text: str, phrases: Iterable[str]) -> bool:
    blob = (text or "").lower()
    return any(p in blob for p in phrases)


def _token_hits(text: str, wanted: frozenset[str]) -> int:
    return len(tokenize(text) & wanted)


def _as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v is not None and str(v).strip()]
    text = str(value).strip()
    return [text] if text else []


def _join(parts: Iterable[str]) -> str:
    return " ".join(p for p in parts if p)


@dataclass
class Case:
    official: str = ""
    internal: str = ""
    physics: str = ""
    coroner: str = ""
    authority: str = ""
    evidence: tuple[str, ...] = ()
    destroyed: tuple[str, ...] = ()
    victim_framing: str = ""
    records: str = ""
    contemporaneous: str = ""
    notes: str = ""

    @classmethod
    def from_mapping(cls, obj: dict | None) -> "Case":
        src = obj if isinstance(obj, dict) else {}
        layers = src.get("layers") if isinstance(src.get("layers"), dict) else {}

        def pick(*keys: str) -> str:
            for key in keys:
                if src.get(key) is not None:
                    return check_field(key, str(src.get(key) or ""))
                if layers.get(key) is not None:
                    return check_field(key, str(layers.get(key) or ""))
            return ""

        evidence = _as_list(src.get("evidence") or src.get("independent_evidence"))
        destroyed = _as_list(src.get("destroyed") or src.get("missing"))
        for item in evidence:
            check_field("evidence", item)
        for item in destroyed:
            check_field("destroyed", item)
        return cls(
            official=pick("official", "official_narrative", "narrative"),
            internal=pick("internal", "internal_account", "whistle"),
            physics=pick("physics", "physical", "independent_physics"),
            coroner=pick("coroner", "medical", "forensic"),
            authority=pick("authority", "investigator", "investigating_authority"),
            evidence=tuple(evidence),
            destroyed=tuple(destroyed),
            victim_framing=pick("victim_framing", "framing", "victim"),
            records=pick("records", "paper_trail", "chain_of_custody"),
            contemporaneous=pick("contemporaneous", "at_the_time"),
            notes=pick("notes", "text", "body"),
        )

    def token_count(self) -> int:
        blob = _join(
            [
                self.official,
                self.internal,
                self.physics,
                self.coroner,
                self.authority,
                _join(self.evidence),
                _join(self.destroyed),
                self.victim_framing,
                self.records,
                self.contemporaneous,
                self.notes,
            ]
        )
        return len(tokenize(blob))

    def canonical_json(self) -> str:
        return json.dumps(
            {
                "authority": self.authority,
                "contemporaneous": self.contemporaneous,
                "coroner": self.coroner,
                "destroyed": list(self.destroyed),
                "evidence": list(self.evidence),
                "internal": self.internal,
                "notes": self.notes,
                "official": self.official,
                "physics": self.physics,
                "records": self.records,
                "victim_framing": self.victim_framing,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def input_sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def _independent_evidence(case: Case) -> list[str]:
    """Items that are not a restatement of the official narrative.

    Official narrative is never evidence.
    """
    official = tokenize(case.official)
    kept: list[str] = []
    for item in case.evidence:
        tokens = tokenize(item)
        if not tokens:
            continue
        if official and jaccard(tokens, official) >= 0.85:
            continue
        kept.append(item)
    if case.physics.strip():
        kept.append(case.physics)
    if case.internal.strip() and official:
        if jaccard(tokenize(case.internal), official) < 0.7:
            kept.append(case.internal)
    elif case.internal.strip() and not official:
        kept.append(case.internal)
    return kept


def _score_p1(case: Case) -> tuple[float, list[str]]:
    flags: list[str] = []
    second = _join([case.internal, case.physics, case.contemporaneous])
    official_only = bool(case.official.strip()) and not second.strip()
    if official_only:
        flags.append("official_narrative_only")
        return 0.72, flags
    if not case.official.strip() or not second.strip():
        return 0.0, flags
    overlap = jaccard(tokenize(case.official), tokenize(second))
    if overlap >= 0.7:
        return _clip(1.0 - overlap), flags
    return _clip(1.0 - overlap), flags


def _score_p2(case: Case) -> float:
    coroner = case.coroner.strip()
    authority = case.authority.strip()
    loop_text = _join([coroner, authority, case.notes])
    phrase = _has_phrase(loop_text, LOOP_PHRASES)
    hits = _token_hits(loop_text, LOOP_TOKENS)
    independent_med = bool(case.physics.strip()) or any(
        "independent" in item.lower() and ("medical" in item.lower() or "hospital" in item.lower() or "lab" in item.lower() or "chemistry" in item.lower() or "clinical" in item.lower())
        for item in case.evidence
    )
    if coroner and authority:
        overlap = jaccard(tokenize(coroner), tokenize(authority))
        base = 0.35 + 0.5 * overlap
        if phrase or hits:
            base = max(base, 0.7)
        if independent_med:
            base *= 0.45
        return _clip(base)
    if authority and not coroner and (phrase or hits):
        return 0.45 if not independent_med else 0.2
    return 0.0


def _score_p3(case: Case) -> float:
    listed = len(case.destroyed)
    blob = _join([_join(case.destroyed), case.records, case.notes, case.internal])
    hits = _token_hits(blob, DESTROY_TOKENS)
    phrases = sum(1 for p in DESTROY_PHRASES if p in blob.lower())
    if listed == 0 and hits == 0 and phrases == 0:
        return 0.0
    raw = 0.22 * listed + 0.12 * hits + 0.18 * phrases
    return _clip(min(1.0, 0.35 + raw) if (listed or phrases or hits >= 2) else raw)


def _score_p4(case: Case) -> float:
    framing = _join([case.victim_framing, case.official, case.notes])
    hits = _token_hits(framing, BLAME_TOKENS)
    phrases = sum(1 for p in BLAME_PHRASES if p in framing.lower())
    if hits == 0 and phrases == 0:
        return 0.0
    support = _join([case.physics, _join(case.evidence)])
    supported = False
    if support.strip():
        # Independent support for the framing itself — rare and must be explicit.
        supported = jaccard(tokenize(case.victim_framing), tokenize(support)) >= 0.5
    raw = _clip(0.28 * hits + 0.35 * phrases + (0.25 if hits else 0.0))
    if supported:
        raw *= 0.35
    return _clip(raw)


def _score_p5(case: Case) -> float:
    blob = _join([case.records, case.notes, _join(case.destroyed)])
    hits = _token_hits(blob, ERASURE_TOKENS)
    phrases = sum(1 for p in ERASURE_PHRASES if p in blob.lower())
    empty_records = bool(case.official.strip()) and not case.records.strip()
    if empty_records:
        phrases += 1
    if hits == 0 and phrases == 0 and not empty_records:
        return 0.0
    toks = tokenize(blob)
    custody_broken = (
        "chain" in toks
        and "custody" in toks
        and ({"broken", "gap", "gaps", "missing"} & toks)
    )
    raw = 0.2 * hits + 0.22 * phrases + (0.25 if custody_broken else 0.0)
    if empty_records:
        raw = max(raw, 0.4)
    return _clip(raw)


def _score_e(case: Case, official_only: bool) -> tuple[float, list[str]]:
    flags: list[str] = []
    independent = _independent_evidence(case)
    physics = bool(case.physics.strip())
    e = 0.12 * min(len(independent), 6)
    if physics:
        e += 0.35
    if case.contemporaneous.strip():
        e += 0.1
    if official_only or (case.official.strip() and not independent and not physics):
        flags.append("poison_suspicion")
        e = min(e, 0.22)
    # Official narrative never raises E.
    return _clip(e), flags


def _score_c(case: Case) -> float:
    kinds = 0
    if case.physics.strip():
        kinds += 1
    if _independent_evidence(case):
        kinds += 1
    if case.internal.strip():
        kinds += 1
    if case.contemporaneous.strip():
        kinds += 1
    return _clip(kinds / 4.0)


def _score_t(case: Case) -> float:
    if case.contemporaneous.strip():
        t = 0.85
    elif case.internal.strip():
        t = 0.45
    else:
        t = 0.15 if case.official.strip() else 0.0
    after = _has_phrase(
        _join([case.official, case.notes, case.records]), AFTER_FACT_PHRASES
    )
    if after:
        t *= 0.5
    return _clip(t)


def _score_d(case: Case) -> float:
    parts = [
        bool(case.records.strip()),
        bool(case.physics.strip()),
        bool(case.internal.strip()),
        bool(_independent_evidence(case)),
        bool(case.contemporaneous.strip()),
    ]
    return _clip(sum(1 for p in parts if p) / 5.0)


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na < MIN_VECTOR_NORM or nb < MIN_VECTOR_NORM:
        return 0.0
    return _clip(dot / (na * nb))


def _plain(sp: dict[str, float], ssi: float, pc: float, flags: list[str]) -> str:
    if ssi < 0.25 and not flags:
        return (
            "No structural pattern rose above the quiet line. A few matching "
            "words are not a pattern. SPRE stays quiet on purpose."
        )
    bits = []
    if "official_narrative_only" in flags:
        bits.append(
            "Only the official story was given. That story is not treated as evidence."
        )
    if "poison_suspicion" in flags:
        bits.append(
            "Independent evidence and physics are thin, so confidence stays low."
        )
    raised = [k for k in ("p1", "p2", "p3", "p4", "p5") if sp[k] >= CUE_FLOOR]
    if raised:
        labels = ", ".join(P_LABELS[k] for k in raised)
        bits.append(f"Structural cues that lined up: {labels}.")
    bits.append(
        f"Similarity to past confirmed failure-shapes is {ssi:.2f}. "
        f"Confidence (similarity times independent evidence) is {pc:.2f}."
    )
    bits.append(
        "This is a shape match, not a verdict. Nobody is named guilty."
    )
    return " ".join(bits)


@dataclass
class SpreReport:
    case: Case
    p1: float
    p2: float
    p3: float
    p4: float
    p5: float
    e: float
    c: float
    t: float
    d: float
    ssi: float
    pc: float
    flags: tuple[str, ...]
    nearest_training: dict
    plain: str
    input_sha256: str
    version: str = ENGINE_VERSION
    limitation: str = LIMITATION
    extra: dict = field(default_factory=dict)

    def vector(self) -> list[float]:
        return [self.p1, self.p2, self.p3, self.p4, self.p5]

    def to_dict(self) -> dict:
        return {
            "schema": SCHEMA_REPORT,
            "version": self.version,
            "author": "Aziel Eliab",
            "sp": {
                "p1": self.p1,
                "p2": self.p2,
                "p3": self.p3,
                "p4": self.p4,
                "p5": self.p5,
                "e": self.e,
                "c": self.c,
                "t": self.t,
                "d": self.d,
            },
            "labels": dict(P_LABELS),
            "notes": dict(P_NOTES),
            "ssi": self.ssi,
            "pc": self.pc,
            "flags": list(self.flags),
            "nearest_training": self.nearest_training,
            "plain": self.plain,
            "kid_plain": self.plain,
            "input_sha256": self.input_sha256,
            "limitation": self.limitation,
            "advisory": True,
            "asserts_guilt": False,
            "asserts_conspiracy": False,
            "training_set": "historically_confirmed_failures_only",
            "official_narrative_is_evidence": False,
            "clce_type_d": "label_only_not_malice",
        }


def _raw_patterns(case: Case) -> tuple[dict[str, float], list[str]]:
    p1, flags = _score_p1(case)
    p2 = _score_p2(case)
    p3 = _score_p3(case)
    p4 = _score_p4(case)
    p5 = _score_p5(case)
    official_only = "official_narrative_only" in flags
    e, eflags = _score_e(case, official_only)
    flags.extend(eflags)
    c = _score_c(case)
    t = _score_t(case)
    d = _score_d(case)
    return {
        "p1": p1,
        "p2": p2,
        "p3": p3,
        "p4": p4,
        "p5": p5,
        "e": e,
        "c": c,
        "t": t,
        "d": d,
    }, flags


def _apply_anti_apophenia(ssi: float, vec: list[float], token_count: int) -> float:
    cues = sum(1 for x in vec if x >= CUE_FLOOR)
    if token_count < MIN_TOKENS_FOR_SSI:
        ssi *= 0.30
    if cues < MIN_CUES:
        ssi *= 0.50
    if sum(vec) < WEAK_CUE_SUM:
        ssi *= 0.40
    return _clip(ssi)


def pattern_vector(case: Case) -> list[float]:
    sp, _ = _raw_patterns(case)
    return [sp["p1"], sp["p2"], sp["p3"], sp["p4"], sp["p5"]]


def training_vectors() -> list[tuple[str, list[float], str]]:
    out: list[tuple[str, list[float], str]] = []
    for proto in TRAINING_CASES:
        case = Case.from_mapping(proto)
        out.append(
            (
                str(proto["id"]),
                pattern_vector(case),
                str(proto.get("note") or "Structural shape only."),
            )
        )
    return out


def _nearest(vec: list[float]) -> dict:
    best = {"id": None, "similarity": 0.0, "note": "No training shape was close enough to name."}
    for pid, pvec, note in training_vectors():
        sim = _cosine(vec, pvec)
        if sim > float(best["similarity"]):
            best = {
                "id": pid,
                "similarity": round(sim, 6),
                "note": (
                    f"{note} Testing reports structural similarity only. "
                    "This is not an identification and not a charge."
                ),
            }
    return best


def score(payload: dict | Case | None = None, **fields: object) -> SpreReport:
    """Score a SPRE case. Accepts a mapping, Case, or keyword fields."""
    if isinstance(payload, Case):
        case = payload
    elif isinstance(payload, dict):
        merged = dict(payload)
        merged.update({k: v for k, v in fields.items() if v is not None})
        case = Case.from_mapping(merged)
    else:
        case = Case.from_mapping(fields)
    # Size guard on joined notes already applied per field.
    if len(case.official) > MAX_FIELD_CHARS:
        raise ValueError("official exceeds size limit")
    sp, flags = _raw_patterns(case)
    vec = [sp["p1"], sp["p2"], sp["p3"], sp["p4"], sp["p5"]]
    nearest = _nearest(vec)
    ssi = _apply_anti_apophenia(float(nearest["similarity"]), vec, case.token_count())
    # Official-only without independents cannot claim high confidence.
    if "official_narrative_only" in flags:
        ssi = min(ssi, 0.55)
    pc = _clip(ssi * sp["e"])
    unique_flags = tuple(dict.fromkeys(flags))
    digest = case.input_sha256()
    plain = _plain(sp, ssi, pc, list(unique_flags))
    return SpreReport(
        case=case,
        p1=sp["p1"],
        p2=sp["p2"],
        p3=sp["p3"],
        p4=sp["p4"],
        p5=sp["p5"],
        e=sp["e"],
        c=sp["c"],
        t=sp["t"],
        d=sp["d"],
        ssi=ssi,
        pc=pc,
        flags=unique_flags,
        nearest_training=nearest,
        plain=plain,
        input_sha256=digest,
    )


def score_from_text(text: str) -> SpreReport:
    """Conservative free-text path. Unlabeled text is notes, not official evidence."""
    return score({"notes": check_field("notes", text or "")})
