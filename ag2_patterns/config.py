"""
AG2 Configuration - Model-Agnostic Setup

Provides OAI_CONFIG_LIST compatible configuration for AG2.
Supports any OpenAI-compatible API (GPT, Claude, Llama, Mistral, Qwen, etc.)

Source: Inspired by Claude Code's model-agnostic API layer.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# OAI_CONFIG_LIST — AG2's canonical way to specify LLM backends.
#
# Users can provide configs via:
#   1. OAI_CONFIG_LIST env var (JSON string)
#   2. OAI_CONFIG_LIST_PATH env var (path to JSON file)
#   3. Programmatic override via `build_config_list()`
# ---------------------------------------------------------------------------

DEFAULT_MODEL = os.getenv("AG2_DEFAULT_MODEL", "gpt-4o")
DEFAULT_BASE_URL = os.getenv("AG2_BASE_URL", None)  # None = OpenAI default
DEFAULT_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_TEMPERATURE = float(os.getenv("AG2_TEMPERATURE", "0"))
DEFAULT_MAX_TOKENS = int(os.getenv("AG2_MAX_TOKENS", "16384"))
DEFAULT_CONTEXT_WINDOW = int(os.getenv("AG2_CONTEXT_WINDOW", "200000"))


def build_config_list(
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    extra: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build an OAI_CONFIG_LIST entry compatible with AG2.

    This is the single source of truth for LLM configuration.
    Swap model/base_url to point at any OpenAI-compatible endpoint.

    Returns:
        A list with one config dict (AG2 convention).
    """
    config: dict[str, Any] = {
        "model": model or DEFAULT_MODEL,
        "api_key": api_key or DEFAULT_API_KEY,
        "temperature": temperature if temperature is not None else DEFAULT_TEMPERATURE,
        "max_tokens": max_tokens or DEFAULT_MAX_TOKENS,
    }
    if base_url or DEFAULT_BASE_URL:
        config["base_url"] = base_url or DEFAULT_BASE_URL
    if extra:
        config.update(extra)
    return [config]


def load_config_list() -> list[dict[str, Any]]:
    """Load OAI_CONFIG_LIST from environment or file.

    Priority:
      1. OAI_CONFIG_LIST env var (JSON string)
      2. OAI_CONFIG_LIST_PATH env var (file path)
      3. Fallback to build_config_list() with env defaults
    """
    raw = os.getenv("OAI_CONFIG_LIST")
    if raw:
        return json.loads(raw)

    path = os.getenv("OAI_CONFIG_LIST_PATH")
    if path and Path(path).exists():
        return json.loads(Path(path).read_text())

    return build_config_list()


def get_llm_config(
    config_list: list[dict[str, Any]] | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    """Build the `llm_config` dict that AG2 agents expect.

    Args:
        config_list: Pre-built config list (or auto-loaded).
        **overrides: Extra keys merged into llm_config (e.g. timeout, seed).

    Returns:
        Dict ready to pass as `llm_config=` to any AG2 agent.
    """
    llm_config: dict[str, Any] = {
        "config_list": config_list or load_config_list(),
        "cache_seed": overrides.pop("cache_seed", None),
    }
    llm_config.update(overrides)
    return llm_config


# ---------------------------------------------------------------------------
# Context window helpers
# ---------------------------------------------------------------------------

def get_context_window(model: str | None = None) -> int:
    """Return the context window size for the current model.

    Source: src/utils/context.ts — getContextWindowForModel()
    """
    env_override = os.getenv("AG2_CONTEXT_WINDOW")
    if env_override:
        return int(env_override)
    return DEFAULT_CONTEXT_WINDOW


def get_max_output_tokens(model: str | None = None) -> int:
    """Return max output tokens for the current model."""
    return DEFAULT_MAX_TOKENS


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cfg = load_config_list()
    print("Loaded config_list:")
    print(json.dumps(cfg, indent=2, default=str))

    llm_cfg = get_llm_config()
    print("\nllm_config for AG2 agents:")
    print(json.dumps(llm_cfg, indent=2, default=str))
