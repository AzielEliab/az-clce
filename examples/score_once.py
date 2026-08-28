#!/usr/bin/env python3
"""Score one R/D/P triple. Advisory only. Inconsistency, not intent."""

from __future__ import annotations

from clce import classify


def main() -> None:
    report = classify(
        r="login button blue submit",
        d="login form submits credentials",
        p="login button submits credentials",
        n="",
    )
    print(f"triple: {report.triple:.4f}")
    print(f"pairwise_avg: {report.pairwise_avg:.4f}")
    print(f"plus: {report.plus:.4f}")
    print(f"band: {report.band}")
    print(f"types: {report.types} primary={report.primary}")
    print(report.limitation)


if __name__ == "__main__":
    main()
