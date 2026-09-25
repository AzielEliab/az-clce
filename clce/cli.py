"""Command-line interface for AZ-CLCE.

    clce
    clce ui
    clce score --r "..." --d "..." --p "..." [--n "..."]
    clce score --import layers.json --export report.json
    clce classify --r ... --d ... --p ... [--n ...]
    clce gate --min 0.7 --r ... --d ... --p ...
    clce doctor
    clce verify-transfer PATH

Human text is the default. Add --json for the same report a program reads.
Author: Aziel Eliab.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Sequence

from clce import __version__
from clce.engine import THRESHOLD, TYPE_LABELS, classify, debug, gate, score
from clce.io import LayerImportError, load_layers, write_export

TOP_HELP = f"""\
clce — compare three descriptions

usage:
  clce
  clce <command> [options]

Compare what something looks like, what was written, and what it
actually does. Author: Aziel Eliab. Version {__version__}.

Commands:
  ui                Open the local page (this computer only)
  score             Compare the three descriptions
  classify          Compare, and name mismatch types A–D
  gate              Exit 0 when the overlap is at least --min
  doctor            Check this install
  version           Print the version

Advanced:
  verify-transfer   Check a file or folder and rescore it

Examples:
  clce ui
  clce score --r "blue login button" --d "the form submits" --p "the button submits"
  clce doctor
  clce score --json --import layers.json

Run clce <command> --help for options.
Add --json when a program should read the result.
"""

WELCOME = """\
AZ-CLCE compares what something looks like, what was written, and what it actually does.

Open the local page:

  clce ui

Also:
  clce doctor     check this install
  clce --help     list commands

Author: Aziel Eliab
"""


class HumanParser(argparse.ArgumentParser):
    """Argparse with git-style top help and plain errors."""

    def __init__(self, *args, top_help: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.top_help = top_help

    def format_help(self) -> str:
        if self.top_help:
            text = self.top_help
            return text if text.endswith("\n") else text + "\n"
        return super().format_help()

    def error(self, message: str) -> None:
        self.exit(2, _friendly_error(self.prog, message) + "\n")


def _friendly_error(prog: str, message: str) -> str:
    choice = re.search(r"invalid choice: '([^']*)'", message)
    if choice:
        bad = choice.group(1)
        if prog == "clce":
            return f'Unknown command "{bad}". Try: clce ui   or   clce --help'
        if prog == "spre":
            return f'Unknown command "{bad}". Try: spre --help   or   spre score --help'
        return f'Unknown command "{bad}". Try: {prog} --help'
    if "required" in message and "path" in message:
        return f"{prog} needs a file or folder.\nTry: {prog} PATH   or   {prog} --help"
    if message.startswith("unrecognized arguments"):
        extra = message.removeprefix("unrecognized arguments:").strip()
        return f'Unknown option "{extra}".\nTry: {prog} --help'
    if "required" in message:
        return f"Missing something this command needs.\n{message}\nTry: {prog} --help"
    return f"{message}\nTry: {prog} --help"


def format_transfer_human(report: dict) -> str:
    """Short reading of a transfer report. The JSON shape is unchanged."""
    if report.get("error") and not report.get("files"):
        return (
            f"Could not check that path: {report['error']}\n"
            "Try: clce verify-transfer PATH   or   clce verify-transfer --help\n"
        )
    lines: list[str] = []
    lines.append("Checked the files." if report.get("ok") else "The check found a problem.")
    count = report.get("file_count")
    if not isinstance(count, int):
        count = len(report.get("files") or [])
    lines.append(f"Files: {count}")
    sha = report.get("package_sha256") or ""
    if sha:
        lines.append(f"Package hash: {sha}")
    issues = report.get("manifest_issues") or []
    if issues:
        lines.append("Issues:")
        for item in issues:
            lines.append(f"  {item}")
    rescore = report.get("rescore") if isinstance(report.get("rescore"), dict) else {}
    clce = rescore.get("clce") if isinstance(rescore, dict) else None
    if isinstance(clce, dict) and "triple" in clce:
        triple = clce["triple"]
        if isinstance(triple, (int, float)):
            lines.append(f"triple: {triple:.4f}" if isinstance(triple, float) else f"triple: {triple}")
        if clce.get("band"):
            lines.append(f"band: {clce['band']}")
    elif isinstance(clce, list) and clce:
        lines.append(f"CLCE rescored files: {len(clce)}")
    lines.append("Full report: add --json")
    return "\n".join(lines) + "\n"


def _build_parser() -> HumanParser:
    parser = HumanParser(
        prog="clce",
        top_help=TOP_HELP,
        description="Compare what something looks like, what was written, and what it actually does.",
    )
    parser.add_argument("--version", action="version", version=f"clce {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=False)

    sub.add_parser("version", help="Print the version.")
    sub.add_parser("help", help="Show this help.")
    p_doc = sub.add_parser("doctor", help="Check this install (no network).")
    p_doc.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print the same check as JSON.",
    )
    p_ui = sub.add_parser(
        "ui",
        help="Open the local page on this computer (127.0.0.1:8845).",
    )
    p_ui.add_argument("--host", default="127.0.0.1", help="This computer only (default 127.0.0.1).")
    p_ui.add_argument("--port", type=int, default=8845, help="Port (default 8845).")

    def _layers(p: argparse.ArgumentParser) -> None:
        p.add_argument("--r", dest="r", default="", help="What it looks like.")
        p.add_argument("--d", dest="d", default="", help="What they wrote.")
        p.add_argument("--p", dest="p", default="", help="What it actually does.")
        p.add_argument("--n", dest="n", default="", help="Missing pieces (optional).")
        p.add_argument(
            "--import",
            dest="import_path",
            default=None,
            metavar="FILE",
            help="Read the four boxes from JSON or labeled .txt.",
        )
        p.add_argument(
            "--export",
            dest="export_path",
            default=None,
            metavar="FILE",
            help="Write report JSON and a human .txt receipt.",
        )
        p.add_argument(
            "--json",
            action="store_true",
            dest="as_json",
            help="Print the full report as JSON.",
        )

    p_score = sub.add_parser(
        "score",
        help="Compare the three descriptions and print how much they overlap.",
        description=(
            "Compare what it looks like (--r), what they wrote (--d), "
            "and what it actually does (--p). Missing pieces (--n) are optional."
        ),
        epilog="Example: clce score --r \"blue login button\" --d \"the form submits\" --p \"the button submits\"",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _layers(p_score)

    p_cls = sub.add_parser(
        "classify",
        help="Compare, and name mismatch types A–D.",
        description=(
            "Same comparison as score, plus mismatch types A, B, C, and D. "
            "Type D is a label for a pattern. It does not say why the pattern is there."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _layers(p_cls)

    p_gate = sub.add_parser(
        "gate",
        help="Exit 0 when the overlap is at least --min (default 0.7).",
        description="Exit 0 when the triple overlap is at least --min. Otherwise exit 1.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _layers(p_gate)
    p_gate.add_argument(
        "--min",
        dest="min_score",
        type=float,
        default=THRESHOLD,
        help="Lowest triple overlap that still passes (default 0.7).",
    )

    p_vt = sub.add_parser(
        "verify-transfer",
        help="Check a file or folder and rescore it.",
        description=(
            "Check every file in PATH and rescore it. "
            "Prints a short summary. Add --json for the full report."
        ),
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


def _layers_from_args(args) -> dict[str, str]:
    layers = {"r": args.r, "d": args.d, "p": args.p, "n": args.n}
    if getattr(args, "import_path", None):
        loaded = load_layers(args.import_path)
        for key in ("r", "d", "p", "n"):
            flag = getattr(args, key, "")
            layers[key] = flag if flag else loaded[key]
        debug(f"loaded --import {args.import_path}")
    return layers


def _maybe_export(args, report) -> None:
    path = getattr(args, "export_path", None)
    if not path:
        return
    json_path, txt_path = write_export(path, report)
    print(f"Wrote {json_path}", file=sys.stderr)
    print(f"Wrote {txt_path}", file=sys.stderr)


def _print_report(report, as_json: bool, *, with_types: bool) -> None:
    if as_json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return
    percent = report.triple * 100
    print(f"Overlap {percent:.0f}%")
    print(report.kid_plain)
    print()
    print(f"triple: {report.triple:.4f}")
    print(f"pairwise_rd: {report.pairwise_rd:.4f}")
    print(f"pairwise_dp: {report.pairwise_dp:.4f}")
    print(f"pairwise_rp: {report.pairwise_rp:.4f}")
    print(f"pairwise_avg: {report.pairwise_avg:.4f}")
    print(f"plus: {report.plus:.4f}")
    print(f"band: {report.band}")
    print(f"kid_plain: {report.kid_plain}")
    print(f"input_sha256: {report.input_sha256}")
    if with_types:
        if report.types:
            labels = ", ".join(f"{c} {TYPE_LABELS[c]}" for c in report.types)
            print(f"types: {labels}")
            print(f"primary: {report.primary} {TYPE_LABELS[report.primary]}")
        else:
            print("types: (none)")
            print("primary: (none)")
        print(f"limitation: {report.limitation}")


def _emit_transfer(args, report: dict) -> None:
    if args.ndjson or args.backfill or args.as_json:
        if args.ndjson or (args.backfill and not args.as_json):
            from clce.transfer import file_records

            lines = [json.dumps(rec, ensure_ascii=False) for rec in file_records(report)]
            if not args.ndjson:
                text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
            else:
                text = "\n".join(lines) + ("\n" if lines else "")
        else:
            text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    else:
        text = format_transfer_human(report)
    if args.out_path:
        from pathlib import Path

        Path(args.out_path).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text if text.endswith("\n") else text + "\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.cmd is None:
        sys.stdout.write(WELCOME if WELCOME.endswith("\n") else WELCOME + "\n")
        return 0

    if args.cmd == "help":
        sys.stdout.write(parser.format_help())
        return 0

    if args.cmd == "version":
        print(f"clce {__version__}")
        return 0

    if args.cmd == "doctor":
        from clce.doctor import doctor_payload, format_doctor, run_doctor

        results, passed = run_doctor()
        if args.as_json:
            print(json.dumps(doctor_payload(results, passed), indent=2, ensure_ascii=False))
        else:
            sys.stdout.write(format_doctor(results, passed))
        return 0 if passed else 1

    if args.cmd == "ui":
        from clce.ui import serve

        try:
            serve(host=args.host, port=args.port)
        except ValueError:
            print(
                "The local page only listens on this computer (127.0.0.1).\nTry: clce ui",
                file=sys.stderr,
            )
            return 2
        except OSError as exc:
            print(
                f"Could not open the local page: {exc}\nTry: clce ui --port 8846",
                file=sys.stderr,
            )
            return 2
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
                f"Could not check that path: {exc}\nTry: clce verify-transfer --help",
                file=sys.stderr,
            )
            return 2
        _emit_transfer(args, report)
        return 0 if report.get("ok") else 1

    try:
        layers = _layers_from_args(args)
    except (LayerImportError, OSError, ValueError) as exc:
        print(f"Could not read layers: {exc}\nTry: clce score --help", file=sys.stderr)
        return 2

    if args.cmd == "score":
        report = score(**layers)
        _print_report(report, args.as_json, with_types=False)
        _maybe_export(args, report)
        return 0

    if args.cmd == "classify":
        report = classify(**layers)
        _print_report(report, args.as_json, with_types=True)
        _maybe_export(args, report)
        return 0

    if args.cmd == "gate":
        passed, report = gate(
            r=layers["r"],
            d=layers["d"],
            p=layers["p"],
            n=layers["n"],
            min_score=args.min_score,
        )
        payload = report.to_dict()
        payload["gate"] = {"min": args.min_score, "passed": passed}
        if args.as_json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            if passed:
                print(f"Gate passed. Overlap is at least {args.min_score}.")
            else:
                print(f"Gate did not pass. Overlap is below {args.min_score}.")
            print()
            _print_report(report, False, with_types=True)
            print(f"gate_min: {args.min_score}")
            print(f"gate: {'PASS' if passed else 'FAIL'}")
        _maybe_export(args, report)
        return 0 if passed else 1

    parser.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
