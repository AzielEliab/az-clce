"""Triad component schema: 0–1 + 0–100, PhysLing slot, corpus merge contract."""

from __future__ import annotations

import json

from clce.engine import score as clce_score
from clce.triad import (
    FORMULA,
    SCHEMA_TRIAD,
    assemble,
    clce_from_mapping,
    schema_doc,
    spre_component,
    triad_from_reports,
)
from clce.transfer import file_records, verify_transfer
from spre.cli import main as spre_main
from spre.engine import score as spre_score
from tests.fixtures import PERFECT


def test_clce_and_spre_emit_triad_component() -> None:
    clce = clce_score(**PERFECT).to_dict()
    assert clce["triad_component"]["id"] == "clce"
    assert clce["triad_component"]["score"] == 1.0
    assert clce["triad_component"]["score_100"] == 100.0
    assert clce["triad_component"]["unit"] == "unit_interval"
    spre = spre_score(
        {
            "official": "The office says the matter is closed and the official story is complete.",
        }
    ).to_dict()
    assert spre["triad_component"]["id"] == "spre"
    assert spre["triad_component"]["verified"] is True
    assert 0.0 <= spre["triad_component"]["score"] <= 1.0
    assert abs(spre["triad_component"]["score"] - (1.0 - spre["pc"])) < 1e-12


def test_physling_slot_keeps_final_null() -> None:
    triad = triad_from_reports(
        clce=clce_score(**PERFECT).to_dict(),
        spre=spre_score({"official": "closed official story only"}).to_dict(),
    )
    assert triad["schema"] == SCHEMA_TRIAD
    assert triad["author"] == "Aziel Eliab"
    assert triad["components"]["physling"]["home"] == "aziel-corpus"
    assert triad["components"]["physling"]["verified"] is False
    assert triad["final"]["ready"] is False
    assert triad["final"]["score"] is None
    assert triad["final"]["verified_count"] == 2


def test_final_ready_when_physling_filled() -> None:
    clce = clce_from_mapping(clce_score(**PERFECT).to_dict())
    spre = spre_component(0.2, ssi=0.4, e=0.5)
    physling = {
        "schema": "aziel.triad.component.v0.3",
        "id": "physling",
        "home": "aziel-corpus",
        "verified": True,
        "score": 0.8,
        "score_100": 80.0,
    }
    triad = assemble(clce=clce, spre=spre, physling=physling)
    assert triad["final"]["ready"] is True
    assert abs(triad["final"]["score"] - (spre["score"] + clce["score"] + 0.8) / 3.0) < 1e-12
    assert triad["final"]["score_100"] is not None
    assert "all_three_verified" in triad["combine_when"]
    assert "physling.score" in FORMULA or "physling" in triad["formula"]


def test_schema_doc_ranges() -> None:
    doc = schema_doc()
    assert doc["range"] == {"min": 0.0, "max": 1.0}
    assert doc["range_100"] == {"min": 0.0, "max": 100.0}
    assert doc["physling_home"] == "aziel-corpus"
    assert doc["author"] == "Aziel Eliab"


def test_verify_transfer_emits_triad(tmp_path) -> None:
    src = tmp_path / "layers.json"
    src.write_text(json.dumps(PERFECT), encoding="utf-8")
    report = verify_transfer(path=src, queue=False)
    assert report["triad"]["components"]["clce"]["verified"] is True
    assert report["triad"]["components"]["clce"]["score"] == 1.0
    assert report["triad"]["components"]["physling"]["verified"] is False
    assert report["files"][0]["triad"]["schema"] == SCHEMA_TRIAD
    recs = file_records(report)
    assert recs[0]["triad"]["components"]["clce"]["score_100"] == 100.0


def test_backfill_older_clce_report(tmp_path) -> None:
    older = {
        "schema": "az-clce.report.v0.2",
        "triple": 0.8,
        "plus": 0.75,
        "pairwise_avg": 0.82,
        "band": "acceptable",
    }
    path = tmp_path / "old.json"
    path.write_text(json.dumps(older), encoding="utf-8")
    report = verify_transfer(path=path, queue=False, backfill=True)
    assert report["backfill"] is True
    assert report["triad"]["components"]["clce"]["score"] == 0.8
    assert report["triad"]["components"]["clce"]["score_100"] == 80.0


def test_spre_score_directory_batch(tmp_path, capsys) -> None:
    (tmp_path / "a.json").write_text(
        json.dumps({"official": "The office says the matter is closed and complete."}),
        encoding="utf-8",
    )
    (tmp_path / "b.json").write_text(json.dumps(PERFECT), encoding="utf-8")
    code = spre_main(["score", "--ndjson", str(tmp_path)])
    out = capsys.readouterr().out.strip().splitlines()
    assert code == 0
    recs = [json.loads(line) for line in out]
    assert len(recs) == 2
    assert all(r["schema"] == "aziel.triad.record.v0.3" for r in recs)
    assert all(r["triad"]["author"] == "Aziel Eliab" for r in recs)
