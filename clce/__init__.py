"""AZ-CLCE: Cross-Layer Consistency Engine.

Detects inconsistency across representation (R), description (D), and
reality (P). Optional negative space N. Jaccard triple, pairwise average,
and CLCE+. Type D is a label, not a finding of malice.

Author: Aziel Eliab, 2026. Apache-2.0.

CLCE detects inconsistency, not intent. Human validation required.
Not a cybersecurity exploit, not a scanner of other people's systems,
not a lie detector. Advisory scores only.

Standalone from ForgeReceipts, ZionPattern, DecisionGATE, AZ-OS,
Glossa Filter.

Forks are welcome and always allowed.
"""

from __future__ import annotations

from clce.engine import (
    ACCEPTABLE,
    HIGH_N_RATIO,
    THRESHOLD,
    TYPE_LABELS,
    VERY_LOW,
    Report,
    band,
    classify,
    gate,
    score,
    tokenize,
)

__version__ = "0.1.0"
__author__ = "Aziel Eliab"
__all__ = [
    "ACCEPTABLE",
    "HIGH_N_RATIO",
    "THRESHOLD",
    "TYPE_LABELS",
    "VERY_LOW",
    "Report",
    "__version__",
    "band",
    "classify",
    "gate",
    "score",
    "tokenize",
]
