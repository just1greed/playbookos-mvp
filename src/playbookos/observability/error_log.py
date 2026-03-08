from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Any

_ERROR_LOG_LOCK = RLock()


def get_error_log_path(path: str | Path | None = None) -> Path:
    if path is not None:
        resolved = Path(path)
    else:
        configured = os.getenv("PLAYBOOKOS_ERROR_LOG_PATH", "data/error_records.jsonl").strip()
        resolved = Path(configured)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def record_error(
    error: Exception | str,
    *,
    component: str,
    operation: str,
    metadata: dict[str, Any] | None = None,
    path: str | Path | None = None,
) -> dict[str, Any]:
    if isinstance(error, Exception):
        error_type = error.__class__.__name__
        message = str(error)
    else:
        error_type = "RecordedError"
        message = str(error)

    entry = {
        "recorded_at": datetime.now(UTC).isoformat(),
        "component": component,
        "operation": operation,
        "error_type": error_type,
        "message": message,
        "metadata": _to_jsonable(metadata or {}),
    }
    log_path = get_error_log_path(path)
    with _ERROR_LOG_LOCK:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    return entry


def list_recorded_errors(*, path: str | Path | None = None) -> list[dict[str, Any]]:
    log_path = get_error_log_path(path)
    if not log_path.exists():
        return []

    items: list[dict[str, Any]] = []
    with _ERROR_LOG_LOCK:
        with log_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped:
                    continue
                items.append(json.loads(stripped))
    return items


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    return value
