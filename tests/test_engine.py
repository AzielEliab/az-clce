"""Engine: tokenize, Jaccard triple, pairwise, CLCE+, bands, empty sets."""

from __future__ import annotations

from clce.engine import THRESHOLD, band, jaccard, score, tokenize
from tests.fixtures import BELOW, PERFECT, TYPE_C_N


def test_tokenize_lowercase_split_non_alnum() -> None:
    assert tokenize("Login-Button, BLUE!") == frozenset({"login", "button", "blue"})
    assert tokenize("") == frozenset()
    assert tokenize(None) == frozenset()  # type: ignore[arg-type]


def test_empty_all_triple_is_one() -> None:
    report = score("", "", "")
    assert report.triple == 1.0
    assert report.pairwise_rd == 1.0
    assert report.pairwise_dp == 1.0
    assert report.pairwise_rp == 1.0
    assert report.plus == 1.0
    assert report.band == "perfect"


def test_empty_union_with_tokens_is_zero() -> None:
    # One layer has tokens, others empty: union non-empty, intersection empty.
    report = score("alpha", "", "")
    assert report.triple == 0.0
    assert jaccard(frozenset({"alpha"}), frozenset(), frozenset()) == 0.0


def test_perfect_alignment() -> None:
    report = score(**PERFECT)
    assert report.triple == 1.0
    assert report.pairwise_rd == 1.0
    assert report.pairwise_dp == 1.0
    assert report.pairwise_rp == 1.0
    assert report.pairwise_avg == 1.0
    assert report.plus == 1.0
    assert report.band == "perfect"


def test_below_0_7() -> None:
    report = score(**BELOW)
    assert report.triple < THRESHOLD
    assert report.band == "structural_inconsistency"


def test_pairwise_average_is_section_5() -> None:
    report = score("a b c", "b c d", "c d e")
    expected = (report.pairwise_rd + report.pairwise_dp + report.pairwise_rp) / 3.0
    assert abs(report.pairwise_avg - expected) < 1e-12


def test_n_reduces_plus_score() -> None:
    base = score(r="login", d="login", p="login", n="")
    with_n = score(**TYPE_C_N)
    assert base.plus == 1.0
    assert with_n.plus < base.plus
    assert with_n.triple == 1.0
    # plus = |inter| / (|union| + |N|) = 2 / (2 + 5) = 2/7
    assert abs(with_n.plus - (2 / 7)) < 1e-12


def test_plus_without_n_equals_triple() -> None:
    report = score("a b", "a b c", "a b")
    assert abs(report.plus - report.triple) < 1e-12


def test_band_perfect_acceptable_inconsistent() -> None:
    assert band(1.0) == "perfect"
    assert band(0.7) == "acceptable"
    assert band(0.85) == "acceptable"
    assert band(0.699) == "structural_inconsistency"


def test_jaccard_identical_sets() -> None:
    s = frozenset({"a", "b"})
    assert jaccard(s, s) == 1.0
    assert jaccard(s, frozenset({"a"})) == 0.5


def test_kid_plain_and_input_sha256() -> None:
    report = score(**PERFECT)
    assert "stories match" in report.kid_plain.lower() or "same words" in report.kid_plain.lower()
    assert len(report.input_sha256) == 64
    assert report.version == "0.3.0"


def test_oversized_field_rejected() -> None:
    import pytest
    from clce.engine import MAX_FIELD_CHARS

    with pytest.raises(ValueError, match="size limit"):
        score(r="a" * (MAX_FIELD_CHARS + 1))
