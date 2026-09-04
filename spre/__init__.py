"""SPRE: Structural Suppression Pattern Recognition Engine.

SP(c) = {P1..P5, E, C, T, D}. SSI and PC = SSI × E.
Training set = historically confirmed failures only.
Testing = structural similarity. Never guilt or conspiracy.

Author: Aziel Eliab, 2026. Apache-2.0.

Official narrative is not evidence. CLCE Type D remains a label, not malice.
"""

from __future__ import annotations

from spre.engine import (
    ENGINE_VERSION,
    LIMITATION,
    SCHEMA_CASE,
    SCHEMA_REPORT,
    Case,
    SpreReport,
    score,
    score_from_text,
)

__version__ = "0.3.0"
__author__ = "Aziel Eliab"
__all__ = [
    "ENGINE_VERSION",
    "LIMITATION",
    "SCHEMA_CASE",
    "SCHEMA_REPORT",
    "Case",
    "SpreReport",
    "__version__",
    "score",
    "score_from_text",
]
