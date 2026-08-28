"""Deterministic layer fixtures for mismatch types A/B/C/D."""

from __future__ import annotations

# Perfect alignment: identical tokens.
PERFECT = {
    "r": "login button submit credentials",
    "d": "login button submit credentials",
    "p": "login button submit credentials",
    "n": "",
}

# Below 0.7: overlapping but not aligned.
BELOW = {
    "r": "alpha beta gamma",
    "d": "gamma delta epsilon",
    "p": "epsilon zeta eta",
    "n": "",
}

# Type A Surface Error: R↔D low, D↔P and R↔P higher.
# R and D share little; both share more with P.
TYPE_A = {
    "r": "login button blue icon",
    "d": "login form green label",
    "p": "login button form works",
    "n": "",
}

# Type B Functional Error: R↔D high, D↔P or R↔P low.
TYPE_B = {
    "r": "login button submit",
    "d": "login button submit",
    "p": "crash error timeout",
    "n": "",
}

# Type C Structural Gap: all pairwise mediocre, triple < 0.7.
TYPE_C = {
    "r": "alpha beta gamma delta",
    "d": "gamma delta epsilon zeta",
    "p": "epsilon zeta eta theta",
    "n": "",
}

# Type C via high N.
TYPE_C_N = {
    "r": "login button",
    "d": "login button",
    "p": "login button",
    "n": "csrf session timeout encryption audit",
}

# Type D LABEL ONLY: high N, D↔P very low, R↔D high.
TYPE_D = {
    "r": "secure login form",
    "d": "secure login form",
    "p": "open redirect leak",
    "n": "csrf session timeout encryption audit",
}
