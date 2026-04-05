from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def find_env_file(start_dir: str | Path | None = None) -> Path | None:
    """Find the nearest `.env` file from the working directory upwards."""
    base_dir = Path(start_dir or Path.cwd()).expanduser().resolve()
    for directory in (base_dir, *base_dir.parents):
        candidate = directory / ".env"
        if candidate.is_file():
            return candidate
    return None


def _parse_env_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    if stripped.startswith("export "):
        stripped = stripped[len("export ") :].strip()

    key, separator, value = stripped.partition("=")
    if not separator:
        return None

    key = key.strip()
    if not key:
        return None

    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"\"", "'"}:
        value = value[1:-1]

    if " #" in value:
        value = value.split(" #", 1)[0].rstrip()

    return key, value


def load_env_file(env_path: str | Path | None = None) -> Path | None:
    """Load environment variables from `.env` without overriding exported values."""
    path = Path(env_path).expanduser().resolve() if env_path else find_env_file()
    if path is None or not path.is_file():
        return None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        parsed = _parse_env_line(raw_line)
        if parsed is None:
            continue

        key, value = parsed
        os.environ.setdefault(key, value)

    logger.debug("Loaded environment variables from %s", path)
    return path
