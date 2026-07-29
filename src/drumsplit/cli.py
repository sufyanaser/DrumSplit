from __future__ import annotations

import argparse
from pathlib import Path

from .engine import separate
from .events import emit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drumsplit",
        description="Split a drum-only recording into Kick, Snare, Cymbals, and Toms.",
    )
    parser.add_argument("input", type=Path, help="Audio file or directory of audio files.")
    parser.add_argument("output", type=Path, help="Output directory.")
    parser.add_argument("--model-dir", type=Path, default=Path("model"))
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        separate(
            input_path=args.input.resolve(),
            output_dir=args.output.resolve(),
            model_dir=args.model_dir.resolve(),
            requested_device=args.device,
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        emit("error", stage="separation", type=type(exc).__name__, message=str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
