"""Transfer verify: structure of every file, SPRE + CLCE rescore, JSON."""

from __future__ import annotations

import json
import tarfile

from clce.cli import main as clce_main
from clce.transfer import verify_transfer
from spre.cli import main as spre_main
from tests.fixtures import PERFECT


def test_verify_layers_json(tmp_path) -> None:
    src = tmp_path / "layers.json"
    src.write_text(json.dumps(PERFECT), encoding="utf-8")
    report = verify_transfer(path=src, queue=True, queue_path=tmp_path / "q.jsonl")
    assert report["ok"] is True
    assert report["schema"] == "az-clce.transfer.v0.3"
    assert report["author"] == "Aziel Eliab"
    assert report["rescore"]["clce"]["triple"] == 1.0
    assert report["tether"]["queued"] is True
    assert report["asserts_guilt"] is False


def test_verify_spre_case(tmp_path) -> None:
    src = tmp_path / "case.json"
    src.write_text(
        json.dumps(
            {
                "official": "The office says the matter is closed and complete.",
                "internal": "",
                "physics": "",
            }
        ),
        encoding="utf-8",
    )
    report = verify_transfer(path=src, queue=False)
    spre = report["rescore"]["spre"]
    assert "official_narrative_only" in spre["flags"]
    assert spre["official_narrative_is_evidence"] is False


def test_verify_directory_and_tar(tmp_path) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "layers.json").write_text(json.dumps(PERFECT), encoding="utf-8")
    (pack / "note.txt").write_text("What it looks like (R): a\nWhat they wrote (D): a\nWhat it actually does (P): a\n", encoding="utf-8")
    report = verify_transfer(path=pack, queue=False)
    assert report["ok"] is True
    assert report["file_count"] == 2

    tar_path = tmp_path / "pack.tar.gz"
    with tarfile.open(tar_path, "w:gz") as archive:
        archive.add(pack / "layers.json", arcname="layers.json")
    tar_report = verify_transfer(path=tar_path, queue=False, direction="download")
    assert tar_report["ok"] is True
    assert tar_report["direction"] == "download"


def test_manifest_hash_mismatch(tmp_path) -> None:
    src = tmp_path / "layers.json"
    src.write_text(json.dumps(PERFECT), encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema": "az-clce.transfer-package.v0.3",
                "files": [{"path": "layers.json", "sha256": "0" * 64}],
            }
        ),
        encoding="utf-8",
    )
    # Directory includes both files.
    report = verify_transfer(path=tmp_path, queue=False)
    assert report["ok"] is False
    assert any("hash mismatch" in i for i in report["manifest_issues"])


def test_cli_clce_verify_transfer(tmp_path, capsys) -> None:
    src = tmp_path / "layers.json"
    src.write_text(json.dumps(PERFECT), encoding="utf-8")
    code = clce_main(["verify-transfer", "--no-queue", str(src)])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["ok"] is True


def test_cli_spre_score_and_verify(tmp_path, capsys) -> None:
    assert spre_main(["version"]) == 0
    assert "spre 0.3.0" in capsys.readouterr().out
    src = tmp_path / "layers.json"
    src.write_text(json.dumps(PERFECT), encoding="utf-8")
    code = spre_main(["verify-transfer", "--no-queue", str(src)])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["ok"] is True
    code = spre_main(
        [
            "score",
            "--json",
            "--official",
            "The office says the matter is closed and the official story is complete.",
        ]
    )
    scored = json.loads(capsys.readouterr().out)
    assert code == 0
    assert scored["asserts_guilt"] is False
    assert "official_narrative_only" in scored["flags"]
