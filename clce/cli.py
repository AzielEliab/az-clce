"""Command-line interface for AZ-CLCE.

    clce version
    clce doctor
    clce ui
    clce score --r "..." --d "..." --p "..." [--n "..."]
    clce score --import layers.json --export report.json
    clce classify --r ... --d ... --p ... [--n ...]
    clce gate --min 0.7 --r ... --d ... --p ...
    clce verify-transfer PATH

Detects inconsistency, not intent. Type D is a label, not malice.
Advisory scores only. Loopback UI. Forks always allowed.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from clce import __version__
from clce.engine import THRESHOLD, TYPE_LABELS, classify, debug, gate, score
from clce.io import LayerImportError, load_layers, write_export


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
    p_doc = sub.add_parser("doctor", help="Self-check: engine, loopback, import/export, limits.")
    p_doc.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print doctor results as JSON.",
    )
    p_ui = sub.add_parser(
        "ui",
        help="Serve the local CLCE UI on 127.0.0.1:8845 (loopback only).",
    )
    p_ui.add_argument("--host", default="127.0.0.1", help="Loopback host (default 127.0.0.1).")
    p_ui.add_argument("--port", type=int, default=8845, help="Port (default 8845).")

    def _layers(p: argparse.ArgumentParser) -> None:
        p.add_argument("--r", dest="r", default="", help="What it looks like (representation).")
        p.add_argument("--d", dest="d", default="", help="What they wrote (description).")
        p.add_argument("--p", dest="p", default="", help="What it actually does (reality).")
        p.add_argument("--n", dest="n", default="", help="Missing pieces (optional negative space).")
        p.add_argument(
            "--import",
            dest="import_path",
            default=None,
            metavar="FILE",
            help="Load layers from JSON or labeled .txt {r,d,p,n}.",
        )
        p.add_argument(
            "--export",
            dest="export_path",
            default=None,
            metavar="FILE",
            help="Write report JSON plus a human .txt receipt (sha256 of inputs).",
        )
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
        "--out",
        dest="out_path",
        default=None,
        metavar="FILE",
        help="Write JSON or NDJSON to FILE instead of stdout.",
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
    print(f"export_json: {json_path}", file=sys.stderr)
    print(f"export_txt: {txt_path}", file=sys.stderr)


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

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
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0

    if args.cmd == "verify-transfer":
        from clce.transfer import file_records, verify_transfer

        try:
            report = verify_transfer(
                path=args.path,
                direction=args.direction,
                queue=not args.no_queue,
                backfill=args.backfill,
            )
        except (OSError, ValueError) as exc:
            print(f"verify-transfer error: {exc}", file=sys.stderr)
            return 2
        if args.ndjson or args.backfill:
            lines = [json.dumps(rec, ensure_ascii=False) for rec in file_records(report)]
            if not args.ndjson:
                text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
            else:
                text = "\n".join(lines) + ("\n" if lines else "")
        else:
            text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if args.out_path:
            from pathlib import Path

            Path(args.out_path).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text if text.endswith("\n") else text + "\n")
        return 0 if report.get("ok") else 1

    try:
        layers = _layers_from_args(args)
    except (LayerImportError, OSError, ValueError) as exc:
        print(f"import error: {exc}", file=sys.stderr)
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
            _print_report(report, False, with_types=True)
            print(f"gate_min: {args.min_score}")
            print(f"gate: {'PASS' if passed else 'FAIL'}")
        _maybe_export(args, report)
        return 0 if passed else 1

    parser.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
