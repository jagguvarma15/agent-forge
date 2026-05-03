"""Anthropic API integration: send the assembled prompt and return raw text.

The Anthropic client is created via ``_make_client`` so tests can monkeypatch
the seam and supply canned responses.
"""

from __future__ import annotations

import importlib.resources as resources
import time
from typing import Any, Protocol, cast

import anthropic
import yaml
from pydantic import BaseModel

from agent_forge.config import Config
from agent_forge.context import AssembledContext

PROMPTS_PACKAGE = "agent_forge.prompts"
SYSTEM_PROMPT_FILE = "system.md"
USER_TEMPLATE_FILE = "user_template.md"
REPAIR_TEMPLATE_FILE = "repair.md"


class GenerationRequest(BaseModel):
    project_name: str
    target_language: str
    framework: str
    assembled_context: AssembledContext
    language_hints: dict[str, Any]


class _MessagesClient(Protocol):
    def create(self, **kwargs: Any) -> Any: ...


class _AnthropicLike(Protocol):
    @property
    def messages(self) -> _MessagesClient: ...


def _make_client(config: Config) -> _AnthropicLike:
    """Construct the Anthropic SDK client. Test seam."""
    return cast(
        _AnthropicLike,
        anthropic.Anthropic(api_key=config.anthropic_api_key),
    )


def _load_prompt(filename: str) -> str:
    return resources.files(PROMPTS_PACKAGE).joinpath(filename).read_text(encoding="utf-8")


def _render_user_message(req: GenerationRequest) -> str:
    template = _load_prompt(USER_TEMPLATE_FILE)
    hints_yaml = yaml.safe_dump(req.language_hints, sort_keys=False).strip()
    # Use str.replace because the template contains literal `{` / `}` for the
    # JSON example block.
    rendered = (
        template.replace("{project_name}", req.project_name)
        .replace("{target_language}", req.target_language)
        .replace("{language_hints_yaml}", hints_yaml)
        .replace("{assembled_context}", req.assembled_context.body)
    )
    return rendered


def _render_repair_message(raw_response: str, validation_error: str) -> str:
    template = _load_prompt(REPAIR_TEMPLATE_FILE)
    return template.replace("{validation_error}", validation_error).replace(
        "{raw_response}", raw_response
    )


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, anthropic.RateLimitError):
        return True
    if isinstance(exc, anthropic.APIStatusError):
        status = getattr(exc, "status_code", None)
        return status is not None and 500 <= status < 600
    if isinstance(exc, anthropic.APIConnectionError):
        return True
    return False


def _extract_text(response: Any) -> str:
    """Extract concatenated text from an Anthropic ``Message`` response."""
    parts: list[str] = []
    for block in getattr(response, "content", []) or []:
        text = getattr(block, "text", None)
        if isinstance(text, str):
            parts.append(text)
        elif isinstance(block, dict) and isinstance(block.get("text"), str):
            parts.append(block["text"])
    return "".join(parts)


def _call_with_retry(
    client: _AnthropicLike,
    *,
    config: Config,
    system_blocks: list[dict[str, Any]],
    user_message: str,
) -> str:
    delays = [1.0, 2.0, 4.0]
    last_exc: BaseException | None = None
    for attempt in range(len(delays) + 1):
        try:
            response = client.messages.create(
                model=config.model,
                max_tokens=config.max_tokens,
                system=system_blocks,
                messages=[{"role": "user", "content": user_message}],
            )
            return _extract_text(response)
        except Exception as exc:
            last_exc = exc
            if attempt >= len(delays) or not _is_retryable(exc):
                raise
            time.sleep(delays[attempt])
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("unreachable")


def _system_blocks() -> list[dict[str, Any]]:
    system_text = _load_prompt(SYSTEM_PROMPT_FILE)
    return [
        {
            "type": "text",
            "text": system_text,
            "cache_control": {"type": "ephemeral"},
        }
    ]


def generate(req: GenerationRequest, config: Config) -> str:
    """Send the assembled prompt to the Anthropic API and return raw text."""
    client = _make_client(config)
    user_message = _render_user_message(req)
    return _call_with_retry(
        client,
        config=config,
        system_blocks=_system_blocks(),
        user_message=user_message,
    )


def repair(raw_response: str, validation_error: str, config: Config) -> str:
    """Ask the model to repair a previous invalid response."""
    client = _make_client(config)
    user_message = _render_repair_message(raw_response, validation_error)
    return _call_with_retry(
        client,
        config=config,
        system_blocks=_system_blocks(),
        user_message=user_message,
    )
