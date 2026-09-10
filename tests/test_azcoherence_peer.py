"""AZ-CLCE ↔ AZCoherence Softwares peer cross-map.

Separate products. Do not merge engines. CLCE is not Coherence.
AKM-TRIAD-1.0 stays fabric. Identity: Aziel Eliab only.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "workers/download-tracker/src/index.js").read_text(encoding="utf-8")
CITE = (ROOT / "workers/download-tracker/src/cite.js").read_text(encoding="utf-8")
WRANGLER = (ROOT / "workers/download-tracker/wrangler.toml").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
WORKER_README = (ROOT / "workers/download-tracker/README.md").read_text(encoding="utf-8")
CONTRIBUTING = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")


def test_cite_module_peer_azcoherence() -> None:
    assert 'export const AZCOHERENCE_SLUG = "azcoherence"' in CITE
    assert "https://azcoherence-download-tracker.vibelock.workers.dev" in CITE
    assert "https://github.com/AzielEliab/AZCoherence" in CITE
    assert "fraggate_slug: AZCOHERENCE_SLUG" in CITE
    assert 'fraggate_via: "aziel-runtime"' in CITE
    assert "separate_product: true" in CITE
    assert "merged: false" in CITE
    assert "Peer Softwares product" in CITE
    assert "CLCE is not Coherence" in CITE
    assert "Not a Softwares slug" in CITE
    assert "AKM-TRIAD-1.0" in CITE
    assert "Aziel Eliab only" in CITE
    assert "export function citePayload" in CITE
    assert "export function llmsTxt" in CITE
    assert "export function peerListHtml" in CITE
    assert "peers: PEERS" in CITE
    assert "peer_softwares: [AZCOHERENCE_PEER]" in CITE


def test_worker_serves_cite_and_llms() -> None:
    assert 'from "./cite.js"' in INDEX
    assert "citePayload()" in INDEX
    assert "llmsTxt()" in INDEX
    assert "peerListHtml()" in INDEX
    assert '"/llms.txt"' in INDEX
    assert '"/llms.txt"' in WRANGLER
    assert '"/cite.json"' in WRANGLER
    assert "azcoherence" in INDEX
    assert "separate Softwares products" in CITE
    assert "do not merge" in CITE.lower()


def test_docs_cite_peer_separate_product() -> None:
    for text in (README, SKILL, WORKER_README, CONTRIBUTING):
        assert "AZCoherence" in text
        assert "azcoherence" in text
        assert "https://azcoherence-download-tracker.vibelock.workers.dev/" in text
        assert "https://github.com/AzielEliab/AZCoherence" in text
        assert "peer" in text.lower()
        assert "separate" in text.lower()
        assert "do not merge" in text.lower() or "Do not merge" in text
        assert "CLCE is not Coherence" in text
        assert "AKM-TRIAD-1.0" in text
        assert "Aziel Eliab" in text


def test_skill_markdown_embed_matches_peer() -> None:
    assert "FragGate slug azcoherence" in INDEX
    assert "peer Softwares product" in INDEX
    assert "CLCE is not Coherence" in INDEX
    assert "https://github.com/AzielEliab/AZCoherence" in INDEX
    assert "https://azcoherence-download-tracker.vibelock.workers.dev/" in INDEX


def test_engines_not_merged() -> None:
    assert "import * as azcoherence" not in INDEX
    assert "from './azcoherence" not in INDEX
    assert "from \"./azcoherence" not in CITE
    assert "CLCE is not Coherence" in CITE
    assert "merged: false" in CITE
    # Isolation: do not pull DecisionGATE into this Worker cite surface.
    assert "decisiongate" not in CITE.lower()
    assert "decisiongate" not in INDEX.lower()
