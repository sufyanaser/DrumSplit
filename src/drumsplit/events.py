from __future__ import annotations

import json
import sys
from typing import Any, TextIO


def emit(event: str, *, stream: TextIO | None = None, **payload: Any) -> None:
    """Write one machine-readable JSONL event when a text stream is available.

    PyInstaller windowed applications set ``sys.stdout`` and ``sys.stderr`` to
    ``None``. Resolving the stream at call time avoids capturing that invalid
    value and lets the desktop UI run without a console.
    """
    target = stream if stream is not None else sys.stdout
    if target is None:
        return

    message = {"event": event, **payload}
    target.write(json.dumps(message, ensure_ascii=False) + "\n")
    target.flush()
