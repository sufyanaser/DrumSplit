from __future__ import annotations

import argparse
from pathlib import Path

import gdown

from .events import emit

MODEL_FILE_ID = "1-Dm666ScPkg8Gt2-lK3Ua0xOudWHZBGC"
MODEL_NAME = "49469ca8"


def download_model(model_dir: Path, force: bool = False) -> Path:
    model_dir.mkdir(parents=True, exist_ok=True)
    existing = list(model_dir.glob("*.th"))
    if existing and not force:
        emit("model_ready", path=str(existing[0]), cached=True)
        return existing[0]

    output = model_dir / "drumsep_model.th"
    emit("model_download_started", file_id=MODEL_FILE_ID, output=str(output))
    result = gdown.download(id=MODEL_FILE_ID, output=str(output), quiet=False)
    if result is None or not output.exists() or output.stat().st_size == 0:
        raise RuntimeError("Model download failed or produced an empty file.")
    emit("model_ready", path=str(output), cached=False, bytes=output.stat().st_size)
    return output


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
