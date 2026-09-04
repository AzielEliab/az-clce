"""AzielTether hooks: hash-chain queue, scopes, no VPN."""

from __future__ import annotations

from clce.mesh import (
    GENESIS_PREV,
    MESH_NOTE,
    append_queue,
    make_item,
    mesh_status,
    offline_forced,
    verify_queue,
)


def test_hash_chain_and_verify(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("CLCE_OFFLINE", "1")
    q = tmp_path / "q.jsonl"
    a = append_queue({"hello": 1}, scope="az-clce", path=q)
    b = append_queue({"hello": 2}, scope="spre", path=q)
    assert a["prev_hash"] == GENESIS_PREV
    assert b["prev_hash"] == a["hash"]
    assert a["scope"] == "az-clce"
    assert b["scope"] == "spre"
    checked = verify_queue(q)
    assert checked["ok"] is True
    assert checked["items"] == 2
    assert "Not a VPN" in MESH_NOTE or "not a VPN" in MESH_NOTE.lower()
    assert "MirageGrid" in MESH_NOTE


def test_broken_chain_detected(tmp_path) -> None:
    q = tmp_path / "q.jsonl"
    item = make_item({"x": 1}, scope="az-clce", prev_hash=GENESIS_PREV)
    item["prev_hash"] = "1" * 64
    q.write_text(__import__("json").dumps(item) + "\n", encoding="utf-8")
    checked = verify_queue(q)
    assert checked["ok"] is False
    assert checked["broken"]


def test_offline_forced(monkeypatch) -> None:
    monkeypatch.setenv("CLCE_OFFLINE", "1")
    assert offline_forced() is True
    status = mesh_status(probe=False)
    assert status["vpn"] is False
    assert status["miragegrid"] is False
    assert status["author"] == "Aziel Eliab"
