"""This tree is AZ-CLCE only. Not merged into sibling products."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "clce"

FORBIDDEN_ROOTS = frozenset(
    {
        "forgereceipts",
        "zionpattern",
        "zion_pattern",
        "zion_pattern_solver",
        "decisiongate",
        "azos",
        "az_os",
        "veillock",
        "vibelock",
        "godlock",
        "codelock",
        "shadowlock",
        "temporallock",
        "staticclock",
        "miragegrid",
        "glossafilter",
    }
)


def _root_of(name: str) -> str:
    return name.split(".")[0].lower().replace("-", "_")


def test_package_never_imports_siblings() -> None:
    import clce  # noqa: F401
    import clce.cli  # noqa: F401
    import clce.engine  # noqa: F401
    import clce.ui  # noqa: F401

    for name in list(sys.modules):
        assert _root_of(name) not in FORBIDDEN_ROOTS


def test_source_imports_isolated() -> None:
    for py in PKG.rglob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert _root_of(alias.name) not in FORBIDDEN_ROOTS
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert _root_of(node.module) not in FORBIDDEN_ROOTS


def test_not_inside_sibling_products() -> None:
    text = str(ROOT)
    assert text.endswith("az-clce") or "/az-clce" in text
    assert "forgereceipts" not in text
    assert "zion-pattern" not in text
    assert "decisiongate" not in text
    assert (PKG / "engine.py").is_file()
    assert not (ROOT / "forgereceipts").exists()
    assert not (ROOT / "decisiongate").exists()
    assert not (ROOT / "glossafilter").exists()


def test_worker_isolated() -> None:
    toml = (ROOT / "workers" / "download-tracker" / "wrangler.toml").read_text(encoding="utf-8")
    assert 'name = "azclce-download-tracker"' in toml
    assert 'account_id = "ac575a9b822bea2bed97d0ab73aed238"' in toml
    assert 'binding = "DOWNLOADS"' in toml
    assert "/count" in toml
    assert "/download" in toml
    assert "/stats" in toml
    src = (ROOT / "workers" / "download-tracker" / "src" / "index.js").read_text(encoding="utf-8")
    assert 'const PROJECT = "azclce"' in src
    assert "az-clce-0.1.0.tar.gz" in src
    assert "azclce|__total__" in src or 'PROJECT + "|__total__"' in src
    assert "Isolated counter" in src
    assert "env.ASSETS.fetch" in src
    assert "private, no-store" in src
    lowered = src.lower().replace("-", "").replace("_", "").replace(" ", "")
    assert "forgereceipts" not in lowered
    assert "zionpattern" not in lowered
    assert "decisiongate" not in lowered
    assert "glossafilter" not in lowered
    assert "staticclock" not in lowered


def test_readme_honest_scope() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "inconsistency, not intent" in readme.lower()
    assert "Type D" in readme
    assert "Human validation" in readme
    assert "lie detector" in readme.lower()
    assert "0.7" in readme
    assert "Forks are welcome" in readme
    assert "azclce-download-tracker.vibelock.workers.dev" in readme
