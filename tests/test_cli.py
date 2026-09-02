"""CLI: version, help lists ui and version, score, classify, gate exit codes, JSON."""

from __future__ import annotations

import json

from clce import __version__
from clce.cli import main
from tests.fixtures import BELOW, PERFECT, TYPE_A, TYPE_B, TYPE_D


def test_cli_version(capsys) -> None:
    assert main(["version"]) == 0
    assert capsys.readouterr().out.strip() == f"clce {__version__}"
    assert __version__ == "0.2.0"


def test_cli_help_lists_ui_and_version() -> None:
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    else:
        raise AssertionError("argparse --help should SystemExit 0")


def test_help_text_contains_ui_and_version(capsys) -> None:
    try:
        main(["--help"])
    except SystemExit:
        pass
    out = capsys.readouterr().out
    assert "ui" in out
    assert "version" in out
    assert "score" in out
    assert "classify" in out
    assert "gate" in out
    assert "doctor" in out


def test_cli_score_json(capsys) -> None:
    code = main(["score", "--json", "--r", PERFECT["r"], "--d", PERFECT["d"], "--p", PERFECT["p"]])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["triple"] == 1.0
    assert payload["band"] == "perfect"
    assert payload["advisory"] is True


def test_cli_score_text(capsys) -> None:
    code = main(["score", "--r", PERFECT["r"], "--d", PERFECT["d"], "--p", PERFECT["p"]])
    out = capsys.readouterr().out
    assert code == 0
    assert "triple:" in out
    assert "plus:" in out
    assert "band: perfect" in out


def test_cli_classify_types(capsys) -> None:
    code = main(
        ["classify", "--json", "--r", TYPE_A["r"], "--d", TYPE_A["d"], "--p", TYPE_A["p"]]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert "A" in payload["types"]
    assert "limitation" in payload


def test_cli_classify_type_b(capsys) -> None:
    code = main(
        ["classify", "--json", "--r", TYPE_B["r"], "--d", TYPE_B["d"], "--p", TYPE_B["p"]]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert "B" in payload["types"]


def test_cli_classify_type_d_label(capsys) -> None:
    args = ["classify", "--json", "--r", TYPE_D["r"], "--d", TYPE_D["d"], "--p", TYPE_D["p"], "--n", TYPE_D["n"]]
    code = main(args)
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["primary"] == "D"
    assert "not intent" in payload["limitation"].lower() or "malice" in payload["limitation"].lower()


def test_gate_exit_0_when_above_min() -> None:
    code = main(["gate", "--min", "0.7", "--r", PERFECT["r"], "--d", PERFECT["d"], "--p", PERFECT["p"]])
    assert code == 0


def test_gate_exit_1_when_below_min() -> None:
    code = main(["gate", "--min", "0.7", "--r", BELOW["r"], "--d", BELOW["d"], "--p", BELOW["p"]])
    assert code == 1


def test_gate_json_includes_passed(capsys) -> None:
    code = main(
        ["gate", "--json", "--min", "0.7", "--r", PERFECT["r"], "--d", PERFECT["d"], "--p", PERFECT["p"]]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["gate"]["passed"] is True
    assert payload["gate"]["min"] == 0.7


def test_cli_score_import_export(tmp_path, capsys) -> None:
    src = tmp_path / "layers.json"
    src.write_text(
        '{"r": "login button submit credentials", "d": "login button submit credentials", '
        '"p": "login button submit credentials", "n": ""}',
        encoding="utf-8",
    )
    out = tmp_path / "report.json"
    code = main(["score", "--json", "--import", str(src), "--export", str(out)])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["triple"] == 1.0
    assert payload["input_sha256"]
    assert out.is_file()
    receipt = out.with_suffix(".txt")
    assert receipt.is_file()
    assert payload["input_sha256"] in receipt.read_text(encoding="utf-8")


def test_cli_help_lists_import_export(capsys) -> None:
    try:
        main(["score", "--help"])
    except SystemExit:
        pass
    out = capsys.readouterr().out
    assert "--import" in out
    assert "--export" in out
