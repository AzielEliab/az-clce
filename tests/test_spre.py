"""SPRE: SP(c), SSI, PC, official-narrative-is-not-evidence, anti-apophenia."""

from __future__ import annotations

from spre import __version__
from spre.engine import LIMITATION, score, score_from_text
from spre.training import NEGATIVE_CONTROLS, TRAINING_CASES


def test_version() -> None:
    assert __version__ == "0.3.0"


def test_limitation_never_guilt() -> None:
    assert "never asserts guilt" in LIMITATION.lower() or "never assert" in LIMITATION.lower()
    assert "not evidence" in LIMITATION.lower()


def test_official_narrative_only_lowers_e_and_flags() -> None:
    report = score(
        {
            "official": (
                "The office says the matter is closed and the official story "
                "is the complete public record of what happened."
            ),
            "evidence": [
                "The office says the matter is closed and the official story "
                "is the complete public record of what happened."
            ],
        }
    )
    assert "official_narrative_only" in report.flags
    assert "poison_suspicion" in report.flags
    assert report.e <= 0.25
    assert report.pc <= report.ssi
    payload = report.to_dict()
    assert payload["asserts_guilt"] is False
    assert payload["asserts_conspiracy"] is False
    assert payload["official_narrative_is_evidence"] is False
    assert payload["clce_type_d"] == "label_only_not_malice"


def test_official_restatement_is_not_evidence() -> None:
    official = "Safe water was supplied to every home after the switch."
    restated = score({"official": official, "evidence": [official]})
    independent = score(
        {
            "official": official,
            "physics": "Independent lab chemistry found lead far above the safety claim.",
            "evidence": ["independent university water tests"],
        }
    )
    assert restated.e < independent.e


def test_two_story_raises_p1() -> None:
    report = score(
        {
            "official": "The water is safe and meets every published rule.",
            "internal": "Internal notes skipped corrosion control and hid failing tests.",
            "physics": "Independent chemistry shows lead and corrosion above the claim.",
        }
    )
    assert report.p1 >= 0.4


def test_negative_controls_stay_quiet() -> None:
    for case in NEGATIVE_CONTROLS:
        report = score(case)
        assert report.ssi < 0.35, (case["id"], report.ssi, report.vector())
        assert report.to_dict()["asserts_guilt"] is False


def test_training_shapes_are_not_identifications() -> None:
    report = score(TRAINING_CASES[0])
    payload = report.to_dict()
    assert payload["asserts_guilt"] is False
    assert "not an identification" in payload["nearest_training"]["note"].lower()
    assert report.ssi > 0.4
    assert "p1" in payload["sp"]


def test_anti_apophenia_short_text() -> None:
    report = score_from_text("maybe odd")
    assert report.ssi < 0.2
    assert "quiet" in report.plain.lower() or report.ssi == 0.0


def test_paper_trail_and_destruction() -> None:
    report = score(
        {
            "official": "All records were kept in the ordinary way.",
            "internal": "The second story says the files were shredded that night.",
            "destroyed": ["shredded diversion papers", "overwritten message traffic"],
            "records": "Chain of custody on cables was broken; pages were shredded.",
        }
    )
    assert report.p3 >= 0.4
    assert report.p5 >= 0.4


def test_victim_blame_without_independent_support() -> None:
    report = score(
        {
            "official": "They were reckless and brought it on themselves.",
            "victim_framing": "Reckless, hysterical, and noncompliant — their own fault.",
            "physics": "Independent measurements do not describe the person at all.",
        }
    )
    assert report.p4 >= 0.4


def test_canonical_sha_stable() -> None:
    a = score({"official": "alpha", "internal": "beta"})
    b = score({"official": "alpha", "internal": "beta"})
    assert a.input_sha256 == b.input_sha256
    assert len(a.input_sha256) == 64
