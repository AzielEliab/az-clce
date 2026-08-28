"""Cross-Layer Consistency Engine.

R, D, P (and optional N) are normalized token sets: lowercase, split on
non-alphanumeric characters.

Paper formulas (AZ-CLCE v1.0 / v2.0, shipped as Aziel Eliab 2026):

- Jaccard triple:  score = |R ∩ D ∩ P| / |R ∪ D ∪ P|
  empty-all → 1.0; empty union with some tokens → 0.0
- Pairwise: R↔D, D↔P, R↔P as Jaccard; Section 5 final = average of three
- CLCE+: plus = |R ∩ D ∩ P| / (|R ∪ D ∪ P| + |N|)
  N = missing expected tokens. Higher N reduces the plus score.
- Threshold: 1.0 perfect; ≥0.7 acceptable; <0.7 structural inconsistency.
  0.7 is the paper's "acceptable" line, not a pass/fail of truth.

Mismatch classification is deterministic. Type D is a LABEL ONLY.
CLCE detects inconsistency, not intent. Never a finding of malice.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

THRESHOLD = 0.7
ACCEPTABLE = THRESHOLD
VERY_LOW = 0.3
HIGH_N_RATIO = 0.5

# Most severe first. Prefer the most severe matching type; include all.
SEVERITY = ("D", "C", "B", "A")

TYPE_LABELS = {
    "A": "Surface Error",
    "B": "Functional Error",
    "C": "Structural Gap",
    "D": "Intentional Obfuscation (label only)",
}

TYPE_NOTES = {
    "A": "R↔D is low while D↔P and R↔P are higher: docs/UI disagree; function is closer to one layer.",
    "B": "R↔D is high while D↔P or R↔P is low: pretty alignment, function diverges.",
    "C": "High |N| relative to the union, or all pairwise mediocre and the triple score is below 0.7.",
    "D": (
        "LABEL ONLY. High N and D↔P very low and R↔D high: representation "
        "matches description while reality and missing-elements diverge. "
        "CLCE detects inconsistency, not intent. This is not a finding of malice."
    ),
}

LIMITATION = (
    "CLCE detects inconsistency, not intent. Type D is a label, not a "
    "finding of malice. Human validation required. Not a cybersecurity "
    "exploit, not a scanner of other people's systems, not a lie detector. "
    "Advisory scores only. Threshold 0.7 is the paper's acceptable line, "
    "not a pass/fail of truth."
)

_SPLIT = re.compile(r"[^a-z0-9]+")


def tokenize(text: str | None) -> frozenset[str]:
    """Lowercase and split on non-alphanumeric characters. Empty → empty set."""
    if not text:
        return frozenset()
    return frozenset(tok for tok in _SPLIT.split(text.lower()) if tok)


def jaccard(*groups: Iterable[str]) -> float:
    """Jaccard of the given token groups.

    Empty-all → 1.0. Non-empty tokens with empty intersection over a
    non-empty union → 0.0.
    """
    sets = [set(g) for g in groups]
    if not any(sets):
        return 1.0
    union: set[str] = set()
    for s in sets:
        union |= s
    if not union:
        return 1.0
    inter = set(sets[0])
    for s in sets[1:]:
        inter &= s
    return len(inter) / len(union)


def _sorted(tokens: Iterable[str]) -> list[str]:
    return sorted(tokens)


@dataclass(frozen=True)
class Report:
    r: str
    d: str
    p: str
    n: str
    tokens_r: frozenset[str]
    tokens_d: frozenset[str]
    tokens_p: frozenset[str]
    tokens_n: frozenset[str]
    triple: float
    pairwise_rd: float
    pairwise_dp: float
    pairwise_rp: float
    pairwise_avg: float
    plus: float
    n_ratio: float
    types: tuple[str, ...]
    primary: str | None
    band: str
    limitation: str = LIMITATION
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        notes = {code: TYPE_NOTES[code] for code in self.types}
        labels = {code: TYPE_LABELS[code] for code in self.types}
        return {
            "r": self.r,
            "d": self.d,
            "p": self.p,
            "n": self.n,
            "tokens": {
                "r": _sorted(self.tokens_r),
                "d": _sorted(self.tokens_d),
                "p": _sorted(self.tokens_p),
                "n": _sorted(self.tokens_n),
            },
            "triple": self.triple,
            "pairwise": {
                "rd": self.pairwise_rd,
                "dp": self.pairwise_dp,
                "rp": self.pairwise_rp,
            },
            "pairwise_avg": self.pairwise_avg,
            "plus": self.plus,
            "n_ratio": self.n_ratio,
            "band": self.band,
            "types": list(self.types),
            "primary": self.primary,
            "type_labels": labels,
            "type_notes": notes,
            "limitation": self.limitation,
            "threshold": THRESHOLD,
            "advisory": True,
        }


def band(triple: float) -> str:
    """Map the triple score onto the paper's three lines."""
    if triple >= 1.0 - 1e-12:
        return "perfect"
    if triple >= THRESHOLD:
        return "acceptable"
    return "structural_inconsistency"


def _plus(inter_triple: int, union_size: int, n_size: int) -> float:
    denom = union_size + n_size
    if denom == 0:
        return 1.0
    return inter_triple / denom


def _n_ratio(n_size: int, union_size: int) -> float:
    return n_size / max(union_size, 1)


def _matching_types(
    rd: float,
    dp: float,
    rp: float,
    triple: float,
    n_ratio: float,
) -> tuple[str, ...]:
    """Return matching type codes, most severe first.

    A Surface Error: R↔D low (<0.7) while D↔P and R↔P are higher.
    B Functional Error: R↔D high (≥0.7) while D↔P or R↔P is low.
    C Structural Gap: high |N| relative to union, or all pairwise
      mediocre and triple score <0.7.
    D Intentional Obfuscation (LABEL ONLY): high N AND D↔P very low
      AND R↔D high. Never a finding of malice.
    """
    high_n = n_ratio >= HIGH_N_RATIO
    matched: list[str] = []

    # D — most severe. Label only.
    if high_n and dp < VERY_LOW and rd >= THRESHOLD:
        matched.append("D")

    # C
    all_mediocre = rd < THRESHOLD and dp < THRESHOLD and rp < THRESHOLD
    if high_n or (all_mediocre and triple < THRESHOLD):
        matched.append("C")

    # B
    if rd >= THRESHOLD and (dp < THRESHOLD or rp < THRESHOLD):
        matched.append("B")

    # A
    if rd < THRESHOLD and dp > rd and rp > rd:
        matched.append("A")

    return tuple(matched)


def score(r: str = "", d: str = "", p: str = "", n: str = "") -> Report:
    """Compute triple, pairwise, CLCE+, band, and mismatch types."""
    tr, td, tp, tn = tokenize(r), tokenize(d), tokenize(p), tokenize(n)
    union = set(tr) | set(td) | set(tp)
    inter = set(tr) & set(td) & set(tp)
    triple = jaccard(tr, td, tp)
    rd = jaccard(tr, td)
    dp = jaccard(td, tp)
    rp = jaccard(tr, tp)
    avg = (rd + dp + rp) / 3.0
    plus = _plus(len(inter), len(union), len(tn))
    ratio = _n_ratio(len(tn), len(union))
    types = _matching_types(rd, dp, rp, triple, ratio)
    primary = types[0] if types else None
    return Report(
        r=r,
        d=d,
        p=p,
        n=n,
        tokens_r=tr,
        tokens_d=td,
        tokens_p=tp,
        tokens_n=tn,
        triple=triple,
        pairwise_rd=rd,
        pairwise_dp=dp,
        pairwise_rp=rp,
        pairwise_avg=avg,
        plus=plus,
        n_ratio=ratio,
        types=types,
        primary=primary,
        band=band(triple),
    )


def classify(r: str = "", d: str = "", p: str = "", n: str = "") -> Report:
    """Same computation as score; named for the classify CLI."""
    return score(r=r, d=d, p=p, n=n)


def gate(
    r: str = "",
    d: str = "",
    p: str = "",
    n: str = "",
    min_score: float = THRESHOLD,
) -> tuple[bool, Report]:
    """Return (passed, report). Passed iff triple score ≥ min_score."""
    report = score(r=r, d=d, p=p, n=n)
    return report.triple >= min_score, report
