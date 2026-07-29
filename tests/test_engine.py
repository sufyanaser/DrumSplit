from __future__ import annotations

from pathlib import Path

import pytest

from drumsplit.engine import detect_device, find_inputs


def test_find_inputs_accepts_supported_file(tmp_path: Path) -> None:
    audio = tmp_path / "drums.wav"
    audio.write_bytes(b"not-a-real-wave")
    assert find_inputs(audio) == [audio]


def test_find_inputs_filters_directory(tmp_path: Path) -> None:
    wav = tmp_path / "a.wav"
    mp3 = tmp_path / "b.mp3"
    txt = tmp_path / "notes.txt"
    wav.write_bytes(b"x")
    mp3.write_bytes(b"x")
    txt.write_text("x", encoding="utf-8")
    assert find_inputs(tmp_path) == [wav, mp3]


def test_find_inputs_rejects_unsupported_file(tmp_path: Path) -> None:
    source = tmp_path / "drums.aac"
    source.write_bytes(b"x")
    with pytest.raises(ValueError, match="Unsupported input format"):
        find_inputs(source)


def test_explicit_cpu_device_is_preserved() -> None:
    assert detect_device("cpu") == "cpu"
