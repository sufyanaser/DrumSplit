from __future__ import annotations

import io

from drumsplit.events import emit


def test_emit_writes_json_line() -> None:
    stream = io.StringIO()
    emit("ready", stream=stream, value=1)
    assert stream.getvalue() == '{"event": "ready", "value": 1}\n'


def test_emit_allows_missing_stdout(monkeypatch) -> None:
    monkeypatch.setattr("sys.stdout", None)
    emit("ready")
