"""Mismatch types A/B/C/D. D is a label, not malice. All matching types listed."""

from __future__ import annotations

from clce.engine import TYPE_LABELS, classify
from tests.fixtures import TYPE_A, TYPE_B, TYPE_C, TYPE_C_N, TYPE_D


def test_type_a_surface_error() -> None:
    report = classify(**TYPE_A)
    assert "A" in report.types
    assert report.pairwise_rd < 0.7
    assert report.pairwise_dp > report.pairwise_rd
    assert report.pairwise_rp > report.pairwise_rd
    from clce.engine import TYPE_LABELS
    assert "malice" not in TYPE_LABELS["A"].lower()


def test_type_b_functional_error() -> None:
    report = classify(**TYPE_B)
    assert "B" in report.types
    assert report.pairwise_rd >= 0.7
    assert report.pairwise_dp < 0.7 or report.pairwise_rp < 0.7


def test_type_c_structural_gap_mediocre() -> None:
    report = classify(**TYPE_C)
    assert "C" in report.types
    assert report.triple < 0.7
    assert report.pairwise_rd < 0.7
    assert report.pairwise_dp < 0.7
    assert report.pairwise_rp < 0.7


def test_type_c_high_n() -> None:
    report = classify(**TYPE_C_N)
    assert "C" in report.types
    assert report.n_ratio >= 0.5


def test_type_d_label_only_not_malice() -> None:
    report = classify(**TYPE_D)
    assert "D" in report.types
    assert report.primary == "D"
    assert report.pairwise_rd >= 0.7
    assert report.pairwise_dp < 0.3
    assert report.n_ratio >= 0.5
    blob = " ".join(report.to_dict()["type_notes"].values()) + report.limitation
    assert "not intent" in blob.lower() or "not a finding of malice" in blob.lower()
    assert "LABEL ONLY" in TYPE_LABELS["D"] or "label only" in TYPE_LABELS["D"].lower()


def test_type_d_includes_all_matching_prefer_severe() -> None:
    report = classify(**TYPE_D)
    # D also matches B (R↔D high, D↔P low) and C (high N).
    assert report.types[0] == "D"
    assert "B" in report.types
    assert "C" in report.types
    assert list(report.types) == sorted(
        report.types, key=lambda c: "DCBA".index(c)
    )


def test_perfect_has_no_mismatch_type() -> None:
    report = classify("same token set", "same token set", "same token set")
    assert report.types == ()
    assert report.primary is None
    assert report.band == "perfect"
