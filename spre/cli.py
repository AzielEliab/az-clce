"""Command-line interface for SPRE.

    spre version
    spre score --official "..." --internal "..." [--physics "..."]
    spre score --import case.json
    spre verify-transfer PATH

Structural similarity only. Never guilt or conspiracy.
Official narrative is not evidence. Author: Aziel Eliab.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from spre import __version__
from spre.engine import score


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spre",
        description=(
            "SPRE — Structural Suppression Pattern Recognition Engine "
            "(Aziel Eliab, 2026). Scores structural similarity to historically "
            "confirmed failures. Never guilt, never conspiracy. Official "
            "narrative is not evidence."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("version", help="Print package version.")

    p_score = sub.add_parser("score", help="Score a SPRE case (advisory).")
    p_score.add_argument("--official", default="", help="Official narrative (not evidence).")
    p_score.add_argument("--internal", default="", help="Internal or contemporaneous account.")
    p_score.add_argument("--physics", default="", help="Independent physical measurements.")
    p_score.add_argument("--coroner", default="", help="Medical / forensic notes.")
    p_score.add_argument("--authority", default="", help="Investigating authority notes.")
    p_score.add_argument("--victim-framing", dest="victim_framing", default="")
    p_score.add_argument("--records", default="", help="Paper trail / chain of custody.")
    p_score.add_argument("--contemporaneous", default="")
    p_score.add_argument("--notes", default="")
    p_score.add_argument(
        "--evidence",
        action="append",
        default=[],
        help="Independent evidence item (repeatable). Official text does not count.",
    )
    p_score.add_argument(
        "--destroyed",
        action="append",
        default=[],
        help="Missing or destroyed item (repeatable).",
    )
    p_score.add_argument("--import", dest="import_path", default=None, metavar="FILE")
    p_score.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print the full report as JSON.",
    )

    p_vt = sub.add_parser(
        "verify-transfer",
        help="Verify every file in PATH, rescore SPRE + CLCE, emit JSON.",
    )
    p_vt.add_argument("path", help="File, directory, or .tar.gz package.")
    p_vt.add_argument(
        "--direction",
        default="local",
        choices=("local", "upload", "download"),
    )
    p_vt.add_argument(
        "--no-queue",
        action="store_true",
        help="Do not append a tether-queue item.",
    )
    return parser


def _print_score(report, as_json: bool) -> None:
    if as_json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return
    payload = report.to_dict()
    print(f"ssi: {payload['ssi']:.4f}")
    print(f"pc: {payload['pc']:.4f}")
    sp = payload["sp"]
    print(
        "sp: "
        + " ".join(f"{k}={sp[k]:.3f}" for k in ("p1", "p2", "p3", "p4", "p5", "e", "c", "t", "d"))
    )
    print(f"flags: {', '.join(payload['flags']) or '(none)'}")
    print(f"plain: {payload['plain']}")
    print(f"input_sha256: {payload['input_sha256']}")
    print(f"limitation: {payload['limitation']}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.cmd == "version":
        print(f"spre {__version__}")
        return 0

    if args.cmd == "score":
        payload: dict = {
            "official": args.official,
            "internal": args.internal,
            "physics": args.physics,
            "coroner": args.coroner,
            "authority": args.authority,
            "victim_framing": args.victim_framing,
            "records": args.records,
            "contemporaneous": args.contemporaneous,
            "notes": args.notes,
            "evidence": list(args.evidence or []),
            "destroyed": list(args.destroyed or []),
        }
        if args.import_path:
            raw = Path(args.import_path).read_text(encoding="utf-8")
            try:
                loaded = json.loads(raw)
            except json.JSONDecodeError as exc:
                print(f"import error: {exc}", file=sys.stderr)
                return 2
            if not isinstance(loaded, dict):
                print("import error: JSON object required", file=sys.stderr)
                return 2
            for key, value in payload.items():
                if value in ("", [], None):
                    continue
                loaded[key] = value
            payload = loaded
        try:
            report = score(payload)
        except ValueError as exc:
            print(f"score error: {exc}", file=sys.stderr)
            return 2
        _print_score(report, args.as_json)
        return 0

    if args.cmd == "verify-transfer":
        from clce.transfer import verify_transfer

        try:
            report = verify_transfer(
                path=args.path,
                direction=args.direction,
                queue=not args.no_queue,
            )
        except (OSError, ValueError) as exc:
            print(f"verify-transfer error: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report.get("ok") else 1

    parser.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
