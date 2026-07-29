from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import soundfile as sf

from .events import emit
from .setup_model import MODEL_NAME

SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg"}
EXPECTED_STEMS = ("kick", "snare", "cymbals", "toms")


@dataclass(frozen=True)
class AudioInfo:
    frames: int
    sample_rate: int
    channels: int

    @property
    def duration(self) -> float:
        return self.frames / self.sample_rate


def inspect_audio(path: Path) -> AudioInfo:
    info = sf.info(str(path))
    return AudioInfo(
        frames=info.frames,
        sample_rate=info.samplerate,
        channels=info.channels,
    )


def detect_device(requested: str) -> str:
    if requested in {"cpu", "cuda"}:
        return requested
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


def find_inputs(path: Path) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported input format: {path.suffix}")
        return [path]
    if path.is_dir():
        files = sorted(
            item
            for item in path.iterdir()
            if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        if not files:
            raise ValueError("Input directory contains no supported audio files.")
        return files
    raise FileNotFoundError(f"Input does not exist: {path}")


def run_demucs(
    input_file: Path,
    output_dir: Path,
    model_dir: Path,
    device: str,
) -> None:
    command = [
        sys.executable,
        "-m",
        "demucs.separate",
        "--repo",
        str(model_dir),
        "-o",
        str(output_dir),
        "-n",
        MODEL_NAME,
        "-d",
        device,
        str(input_file),
    ]
    emit(
        "separation_started",
        input=str(input_file),
        device=device,
        command=command[:-1],
    )
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert process.stdout is not None
    for line in process.stdout:
        line = line.strip()
        if line:
            emit("engine_log", input=str(input_file), message=line)
    return_code = process.wait()
    if return_code != 0:
        raise RuntimeError(f"Demucs exited with code {return_code}.")


def locate_job_output(output_dir: Path, input_file: Path) -> Path:
    candidates = [
        output_dir / MODEL_NAME / input_file.stem,
        output_dir / input_file.stem,
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    matches = list(output_dir.rglob(input_file.stem))
    for match in matches:
        if match.is_dir():
            return match
    raise FileNotFoundError(
        f"Could not locate separated output for {input_file.name}."
    )


def normalize_stems(job_dir: Path, destination: Path) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    exported: list[Path] = []
    for stem in EXPECTED_STEMS:
        matches = [p for p in job_dir.glob("*.wav") if p.stem.lower() == stem]
        if not matches:
            raise FileNotFoundError(f"Expected stem was not generated: {stem}.wav")
        target = destination / f"{stem}.wav"
        shutil.copy2(matches[0], target)
        exported.append(target)
    return exported


def validate_stems(
    source: Path,
    stems: list[Path],
    tolerance_seconds: float = 0.1,
) -> None:
    source_info = inspect_audio(source)
    for stem in stems:
        stem_info = inspect_audio(stem)
        if abs(stem_info.duration - source_info.duration) > tolerance_seconds:
            raise RuntimeError(
                f"Duration mismatch for {stem.name}: {stem_info.duration:.3f}s vs "
                f"{source_info.duration:.3f}s"
            )
        emit(
            "stem_validated",
            stem=str(stem),
            duration=round(stem_info.duration, 3),
            sample_rate=stem_info.sample_rate,
            channels=stem_info.channels,
        )


def separate(
    input_path: Path,
    output_dir: Path,
    model_dir: Path,
    requested_device: str,
) -> None:
    if not model_dir.is_dir() or not any(model_dir.iterdir()):
        raise FileNotFoundError(
            "Model directory is missing or empty. Run drumsplit-setup first."
        )

    inputs = find_inputs(input_path)
    device = detect_device(requested_device)
    emit(
        "environment",
        device=device,
        input_count=len(inputs),
        model_dir=str(model_dir),
    )

    raw_dir = output_dir / ".raw"
    for index, input_file in enumerate(inputs, start=1):
        emit("file_started", index=index, total=len(inputs), input=str(input_file))
        run_demucs(input_file, raw_dir, model_dir, device)
        job_dir = locate_job_output(raw_dir, input_file)
        final_dir = output_dir / input_file.stem
        stems = normalize_stems(job_dir, final_dir)
        validate_stems(input_file, stems)
        emit(
            "file_completed",
            input=str(input_file),
            output=str(final_dir),
            stems=[str(path) for path in stems],
        )

    shutil.rmtree(raw_dir, ignore_errors=True)
    emit("completed", output=str(output_dir), files=len(inputs))
