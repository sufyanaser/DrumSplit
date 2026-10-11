# ruff: noqa: E402, I001
from __future__ import annotations

import os
import sys


def _ensure_standard_streams() -> None:
    """Provide writable streams for libraries running in a windowed executable."""
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")


_ensure_standard_streams()

from drumsplit.gui import main


if __name__ == "__main__":
    raise SystemExit(main())
