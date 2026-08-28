"""Command-line interface for AZ-CLCE.

    clce version
    clce ui
    clce score --r "..." --d "..." --p "..." [--n "..."]
    clce classify --r ... --d ... --p ... [--n ...]
    clce gate --min 0.7 --r ... --d ... --p ...

Detects inconsistency, not intent. Type D is a label, not malice.
Advisory scores only. Loopback UI. Forks always allowed.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from clce import __version__
from clce.engine import THRESHOLD, TYPE_LABELS, classify, gate, score


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="clce",
        description=(
            "AZ-CLCE — Cross-Layer Consistency Engine (Aziel Eliab, 2026). "
            "Detects inconsistency across representation (R), description (D), "
            "and reality (P). Not intent, not a scanner, not a lie detector. "
            "Advisory scores only. Type D is a label, not a finding of malice. "
            "Local UI: `clce ui` at http://127.0.0.1:8845."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("version", help="Print package version.")
    p_ui = sub.add_parser(
        "ui",
        help="Serve the local CLCE UI on 127.0.0.1:8845 (loopback only).",
    )
    p_ui.add_argument("--host", default="127.0.0.1", help="Loopback host (default 127.0.0.1).")
    p_ui.add_argument("--port", type=int, default=8845, help="Port (default 8845).")

    def _layers(p: argparse.ArgumentParser) -> None:
        p.add_argument("--r", dest="r", default="", help="Representation layer (visuals, diagrams, UI).")
        p.add_argument("--d", dest="d", default="", help="Description layer (text, instructions, claims).")
        p.add_argument("--p", dest="p", default="", help="Reality layer (physical or functional truth).")
        p.add_argument("--n", dest="n", default="", help="Optional missing expected tokens (negative space).")
        p.add_argument(
            "--json",
            action="store_true",
            dest="as_json",
            help="Print the full report as JSON.",
        )

    p_score = sub.add_parser(
        "score",
        help="Jaccard triple, pairwise, CLCE+, and band.",
    )
    _layers(p_score)

    p_cls = sub.add_parser(
        "classify",
        help="Score plus mismatch types A/B/C/D (D is a label only).",
    )
    _layers(p_cls)

    p_gate = sub.add_parser(
        "gate",
        help="Exit 0 if triple score ≥ --min (default 0.7), else 1.",
    )
    _layers(p_gate)
    p_gate.add_argument(
        "--min",
        dest="min_score",
        type=float,
        default=THRESHOLD,
        help="Minimum triple score to pass (default 0.7, the paper's acceptable line).",
    )

    return parser


def _print_report(report, as_json: bool, *, with_types: bool) -> None:
    if as_json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return
    print(f"triple: {report.triple:.4f}")
    print(f"pairwise_rd: {report.pairwise_rd:.4f}")
    print(f"pairwise_dp: {report.pairwise_dp:.4f}")
    print(f"pairwise_rp: {report.pairwise_rp:.4f}")
    print(f"pairwise_avg: {report.pairwise_avg:.4f}")
    print(f"plus: {report.plus:.4f}")
    print(f"band: {report.band}")
    if with_types:
        if report.types:
            labels = ", ".join(f"{c} {TYPE_LABELS[c]}" for c in report.types)
            print(f"types: {labels}")
            print(f"primary: {report.primary} {TYPE_LABELS[report.primary]}")
        else:
            print("types: (none)")
            print("primary: (none)")
        print(f"limitation: {report.limitation}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.cmd == "version":
        print(f"clce {__version__}")
        return 0

    if args.cmd == "ui":
        from clce.ui import serve

        try:
            serve(host=args.host, port=args.port)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0

    if args.cmd == "score":
        report = score(r=args.r, d=args.d, p=args.p, n=args.n)
        _print_report(report, args.as_json, with_types=False)
        return 0

    if args.cmd == "classify":
        report = classify(r=args.r, d=args.d, p=args.p, n=args.n)
        _print_report(report, args.as_json, with_types=True)
        return 0

    if args.cmd == "gate":
        passed, report = gate(
            r=args.r,
            d=args.d,
            p=args.p,
            n=args.n,
            min_score=args.min_score,
        )
        payload = report.to_dict()
        payload["gate"] = {"min": args.min_score, "passed": passed}
        if args.as_json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            _print_report(report, False, with_types=True)
            print(f"gate_min: {args.min_score}")
            print(f"gate: {'PASS' if passed else 'FAIL'}")
        return 0 if passed else 1

    parser.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
