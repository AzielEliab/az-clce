"""Command-line interface for SPRE.

    spre
    spre version
    spre score --official "..." --internal "..." [--physics "..."]
    spre score --import case.json
    spre verify-transfer PATH

Human text is the default. Add --json for the same report a program reads.
Author: Aziel Eliab.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from clce.cli import HumanParser, format_transfer_human
from spre import __version__
from spre.engine import score

SPRE_HELP = f"""\
spre — structural similarity

usage:
  spre
  spre <command> [options]

Score how closely a case matches patterns from historically confirmed
failures. Author: Aziel Eliab. Version {__version__}.

Commands:
  score             Score one case, or a folder of cases
  version           Print the version

Advanced:
  verify-transfer   Check a file or folder and rescore it

Examples:
  spre score --official "..." --physics "..."
  spre score --json --import case.json
  spre score --help

Add --json when a program should read the result.
Official narrative is not treated as evidence. See spre score --help.
"""

SPRE_WELCOME = """\
SPRE scores how closely a case matches patterns from historically confirmed failures.

Next:
  spre score --official "..." --physics "..."
  spre --help

Author: Aziel Eliab
"""


def _build_parser() -> HumanParser:
    parser = HumanParser(
        prog="spre",
        top_help=SPRE_HELP,
        description="Score how closely a case matches patterns from historically confirmed failures.",
    )
    parser.add_argument("--version", action="version", version=f"spre {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=False)
    sub.add_parser("version", help="Print the version.")
    sub.add_parser("help", help="Show this help.")

    p_score = sub.add_parser(
        "score",
        help="Score one case, or a folder of cases.",
        description=(
            "Score structural similarity. Official narrative is not treated as evidence. "
            "Add --json for the full report."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
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
    p_score.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Case JSON file or directory of older payloads (batch/backfill).",
    )
    p_score.add_argument("--import", dest="import_path", default=None, metavar="FILE")
    p_score.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print the full report as JSON.",
    )
    p_score.add_argument(
        "--ndjson",
        action="store_true",
        help="One JSON object per file when scoring a directory.",
    )
    p_score.add_argument(
        "--backfill",
        action="store_true",
        help="Treat PATH as a directory of older payloads; emit triad records.",
    )
    p_score.add_argument(
        "--out",
        dest="out_path",
        default=None,
        metavar="FILE",
        help="Write JSON or NDJSON to FILE.",
    )

    p_vt = sub.add_parser(
        "verify-transfer",
        help="Check a file or folder and rescore it.",
        description="Prints a short summary. Add --json for the full report.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
    p_vt.add_argument(
        "--backfill",
        action="store_true",
        help="Batch-score older payloads in a directory or archive for triad merge.",
    )
    p_vt.add_argument(
        "--ndjson",
        action="store_true",
        help="Emit one triad record per file (for corpus backfill).",
    )
    p_vt.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print the full report as JSON.",
    )
    p_vt.add_argument(
        "--out",
        dest="out_path",
        default=None,
        metavar="FILE",
        help="Write the report to FILE instead of the screen.",
    )
    return parser


def _print_score(report, as_json: bool) -> None:
    if as_json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return
    payload = report.to_dict()
    print(payload["plain"])
    print()
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


def _emit_transfer(args, report: dict) -> None:
    from clce.transfer import file_records

    if args.ndjson or args.backfill or args.as_json:
        if args.ndjson:
            text = "\n".join(json.dumps(rec, ensure_ascii=False) for rec in file_records(report))
            text = text + ("\n" if text else "")
        else:
            text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    else:
        text = format_transfer_human(report)
    if args.out_path:
        Path(args.out_path).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text if text.endswith("\n") else text + "\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.cmd is None:
        sys.stdout.write(SPRE_WELCOME if SPRE_WELCOME.endswith("\n") else SPRE_WELCOME + "\n")
        return 0

    if args.cmd == "help":
        sys.stdout.write(parser.format_help())
        return 0

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
        batch_path = args.path or args.import_path
        if batch_path and Path(batch_path).is_dir():
            from clce.transfer import file_records, verify_transfer

            try:
                packed = verify_transfer(
                    path=batch_path,
                    queue=False,
                    backfill=True,
                )
            except (OSError, ValueError) as exc:
                print(f"Could not score that folder: {exc}\nTry: spre score --help", file=sys.stderr)
                return 2
            records = file_records(packed)
            if args.ndjson or args.backfill:
                text = "\n".join(json.dumps(rec, ensure_ascii=False) for rec in records)
                text = text + ("\n" if text else "")
            else:
                text = json.dumps(
                    {"author": "Aziel Eliab", "count": len(records), "records": records, "triad": packed.get("triad")},
                    indent=2,
                    ensure_ascii=False,
                ) + "\n"
            if args.out_path:
                Path(args.out_path).write_text(text, encoding="utf-8")
            else:
                sys.stdout.write(text)
            return 0 if packed.get("ok") else 1
        if args.import_path:
            raw = Path(args.import_path).read_text(encoding="utf-8")
            try:
                loaded = json.loads(raw)
            except json.JSONDecodeError as exc:
                print(f"Could not read that file: {exc}\nTry: spre score --help", file=sys.stderr)
                return 2
            if not isinstance(loaded, dict):
                print("Could not read that file: JSON object required.\nTry: spre score --help", file=sys.stderr)
                return 2
            for key, value in payload.items():
                if value in ("", [], None):
                    continue
                loaded[key] = value
            payload = loaded
        elif args.path:
            raw = Path(args.path).read_text(encoding="utf-8")
            try:
                loaded = json.loads(raw)
            except json.JSONDecodeError as exc:
                print(f"Could not read that file: {exc}\nTry: spre score --help", file=sys.stderr)
                return 2
            if not isinstance(loaded, dict):
                print("Could not read that file: JSON object required.\nTry: spre score --help", file=sys.stderr)
                return 2
            payload = loaded
        try:
            report = score(payload)
        except ValueError as exc:
            print(f"Could not score that case: {exc}\nTry: spre score --help", file=sys.stderr)
            return 2
        if args.out_path:
            Path(args.out_path).write_text(
                json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            return 0
        _print_score(report, args.as_json or args.ndjson)
        return 0

    if args.cmd == "verify-transfer":
        from clce.transfer import verify_transfer

        try:
            report = verify_transfer(
                path=args.path,
                direction=args.direction,
                queue=not args.no_queue,
                backfill=args.backfill,
            )
        except (OSError, ValueError) as exc:
            print(
                f"Could not check that path: {exc}\nTry: spre verify-transfer --help",
                file=sys.stderr,
            )
            return 2
        _emit_transfer(args, report)
        return 0 if report.get("ok") else 1

    parser.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
