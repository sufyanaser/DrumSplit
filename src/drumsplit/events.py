from __future__ import annotations

import json
import sys
from typing import Any, TextIO


def emit(event: str, *, stream: TextIO = sys.stdout, **payload: Any) -> None:
    """Write one machine-readable JSONL event and flush immediately."""
    message = {"event": event, **payload}
    stream.write(json.dumps(message, ensure_ascii=False) + "\n")
    stream.flush()
