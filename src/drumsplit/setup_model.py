from __future__ import annotations

import argparse
import os
from pathlib import Path

import gdown

from .events import emit

MODEL_FILE_ID = "1-Dm666ScPkg8Gt2-lK3Ua0xOudWHZBGC"
MODEL_NAME = "49469ca8"


def _existing_model_files(model_dir: Path) -> list[Path]:
    return sorted(path for path in model_dir.iterdir() if path.is_file() and path.stat().st_size > 0)


def download_model(model_dir: Path, force: bool = False) -> Path:
    model_dir.mkdir(parents=True, exist_ok=True)
    existing = _existing_model_files(model_dir)
    if existing and not force:
        emit("model_ready", path=str(existing[0]), cached=True)
        return existing[0]

    if force:
        for path in existing:
            path.unlink()

    emit("model_download_started", file_id=MODEL_FILE_ID, output_dir=str(model_dir))
    result = gdown.download(
        id=MODEL_FILE_ID,
        output=str(model_dir) + os.sep,
        quiet=False,
    )
    if result is None:
        raise RuntimeError("Model download failed.")

    downloaded = Path(result).resolve()
    if not downloaded.exists() or downloaded.stat().st_size == 0:
        raise RuntimeError("Model download produced a missing or empty file.")

    emit("model_ready", path=str(downloaded), cached=False, bytes=downloaded.stat().st_size)
    return downloaded


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download the DrumSep model checkpoint.")
    parser.add_argument("--model-dir", type=Path, default=Path("model"))
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        download_model(args.model_dir.resolve(), args.force)
        return 0
    except Exception as exc:  # noqa: BLE001
        emit("error", stage="model_setup", message=str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
