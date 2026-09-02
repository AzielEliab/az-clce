"""clce doctor self-check."""

from __future__ import annotations

import json
import os

from clce.cli import main
from clce.doctor import run_doctor


def test_doctor_python_api() -> None:
    results, passed = run_doctor()
    assert passed, results
    names = [name for name, _, _ in results]
    assert "version" in names
    assert "types A-D" in names
    assert "import/export roundtrip" in names
    assert "loopback" in names


def test_cli_doctor(capsys) -> None:
    code = main(["doctor"])
    out = capsys.readouterr().out
    assert code == 0
    assert "all checks passed" in out
    assert "ok  " in out
    assert "0.2.0" in out


def test_cli_doctor_json(capsys) -> None:
    code = main(["doctor", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["ok"] is True
    assert payload["version"] == "0.2.0"


def test_clce_debug_flag(capsys) -> None:
    old = os.environ.get("CLCE_DEBUG")
    os.environ["CLCE_DEBUG"] = "1"
    try:
        from clce.engine import debug, debug_enabled

        assert debug_enabled() is True
        debug("hello-doctor")
    finally:
        if old is None:
            os.environ.pop("CLCE_DEBUG", None)
        else:
            os.environ["CLCE_DEBUG"] = old
    err = capsys.readouterr().err
    assert "[CLCE_DEBUG] hello-doctor" in err
