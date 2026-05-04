"""Simple file-based response caching keyed by request inputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _cache_key(project_name: str, language: str, framework: str, context_body: str) -> str:
    """Produce a stable hash for the generation inputs."""
    payload = json.dumps(
        {"project_name": project_name, "language": language, "framework": framework, "context": context_body},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def get_cached(cache_dir: Path, project_name: str, language: str, framework: str, context_body: str) -> str | None:
    """Return cached response text if it exists, else None."""
    key = _cache_key(project_name, language, framework, context_body)
    path = cache_dir / "responses" / f"{key}.json"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return None


def save_cache(cache_dir: Path, project_name: str, language: str, framework: str, context_body: str, response: str) -> None:
    """Save a successful response to cache."""
    key = _cache_key(project_name, language, framework, context_body)
    responses_dir = cache_dir / "responses"
    responses_dir.mkdir(parents=True, exist_ok=True)
    path = responses_dir / f"{key}.json"
    path.write_text(response, encoding="utf-8")


def _hints_signature(hints: dict[str, Any]) -> str:
    """Not used externally — available for future cache key enrichment."""
    return hashlib.sha256(json.dumps(hints, sort_keys=True).encode()).hexdigest()[:8]
