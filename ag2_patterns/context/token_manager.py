"""
Token Manager — Token counting and budget tracking for AG2 agents.

Extracted from Claude Code's token management system:
- src/utils/tokens.ts — Token counting and estimation functions
- src/query/tokenBudget.ts — Budget tracking and continuation decisions
- src/services/tokenEstimation.ts — Bytes-per-token heuristics

Patterns implemented:
1. Fast token estimation (char-based heuristic, no API call)
2. Accurate token counting via tiktoken
3. Token budget tracking with continuation/stop decisions
4. Per-content-type estimation (code, JSON, images, text)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Literal

import tiktoken


# ---------------------------------------------------------------------------
# Token estimation heuristics (from src/services/tokenEstimation.ts)
# ---------------------------------------------------------------------------

# Default bytes per token by content type
BYTES_PER_TOKEN_DEFAULT = 4       # General text
BYTES_PER_TOKEN_JSON = 2          # JSON is denser
BYTES_PER_TOKEN_CODE = 3          # Code averages ~3
IMAGE_TOKEN_ESTIMATE = 2000       # Fixed estimate per image
DOCUMENT_TOKEN_ESTIMATE = 2000    # Fixed estimate per document

# File extension → bytes-per-token mapping
_EXTENSION_BPT: dict[str, int] = {
    ".json": BYTES_PER_TOKEN_JSON,
    ".jsonl": BYTES_PER_TOKEN_JSON,
    ".xml": BYTES_PER_TOKEN_JSON,
    ".yaml": BYTES_PER_TOKEN_CODE,
    ".yml": BYTES_PER_TOKEN_CODE,
    ".py": BYTES_PER_TOKEN_CODE,
    ".ts": BYTES_PER_TOKEN_CODE,
    ".js": BYTES_PER_TOKEN_CODE,
    ".rs": BYTES_PER_TOKEN_CODE,
    ".go": BYTES_PER_TOKEN_CODE,
    ".java": BYTES_PER_TOKEN_CODE,
    ".c": BYTES_PER_TOKEN_CODE,
    ".cpp": BYTES_PER_TOKEN_CODE,
    ".h": BYTES_PER_TOKEN_CODE,
}


def bytes_per_token_for_file(extension: str) -> int:
    """Return the bytes-per-token heuristic for a file extension.

    Source: src/services/tokenEstimation.ts — bytesPerTokenForFileType()
    """
    return _EXTENSION_BPT.get(extension.lower(), BYTES_PER_TOKEN_DEFAULT)


def rough_token_estimate(text: str, bytes_per_token: int = BYTES_PER_TOKEN_DEFAULT) -> int:
    """Fast token count estimation without calling a tokenizer.

    Source: src/utils/tokens.ts — roughTokenCountEstimation()

    Args:
        text: The text to estimate.
        bytes_per_token: Divisor (lower = more tokens estimated).

    Returns:
        Estimated token count.
    """
    return max(1, len(text.encode("utf-8")) // bytes_per_token)


def rough_token_estimate_for_messages(
    messages: list[dict[str, Any]],
) -> int:
    """Estimate tokens for an entire message list.

    Source: src/utils/tokens.ts — roughTokenCountEstimationForMessages()

    Handles:
    - text content → char-based estimate
    - image_url / image content → IMAGE_TOKEN_ESTIMATE
    - tool_use / tool_result → JSON estimate
    """
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            total += rough_token_estimate(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, str):
                    total += rough_token_estimate(block)
                elif isinstance(block, dict):
                    btype = block.get("type", "")
                    if btype in ("image_url", "image"):
                        total += IMAGE_TOKEN_ESTIMATE
                    elif btype == "text":
                        total += rough_token_estimate(block.get("text", ""))
                    else:
                        # tool_use, tool_result, etc. — use JSON estimate
                        import json
                        total += rough_token_estimate(
                            json.dumps(block), BYTES_PER_TOKEN_JSON
                        )
        # Add overhead for role, name, etc.
        total += 4  # ~4 tokens per message framing
    return total


# ---------------------------------------------------------------------------
# Accurate token counting via tiktoken
# ---------------------------------------------------------------------------

_ENCODER_CACHE: dict[str, tiktoken.Encoding] = {}


def get_encoder(model: str = "gpt-4o") -> tiktoken.Encoding:
    """Get a tiktoken encoder, with caching.

    Falls back to cl100k_base for unknown models.
    """
    if model not in _ENCODER_CACHE:
        try:
            _ENCODER_CACHE[model] = tiktoken.encoding_for_model(model)
        except KeyError:
            _ENCODER_CACHE[model] = tiktoken.get_encoding("cl100k_base")
    return _ENCODER_CACHE[model]


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count tokens accurately using tiktoken.

    Source: src/utils/tokens.ts — countTokensWithAPI()
    (We use tiktoken locally instead of making an API call.)
    """
    enc = get_encoder(model)
    return len(enc.encode(text))


def count_message_tokens(
    messages: list[dict[str, Any]],
    model: str = "gpt-4o",
) -> int:
    """Count tokens for a full message array.

    Source: src/utils/tokens.ts — countMessagesTokensWithAPI()

    Uses tiktoken for text; falls back to heuristic for images/special blocks.
    """
    enc = get_encoder(model)
    total = 0
    for msg in messages:
        # Role token overhead
        total += 4
        content = msg.get("content", "")
        if isinstance(content, str):
            total += len(enc.encode(content))
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, str):
                    total += len(enc.encode(block))
                elif isinstance(block, dict):
                    btype = block.get("type", "")
                    if btype in ("image_url", "image"):
                        total += IMAGE_TOKEN_ESTIMATE
                    elif btype == "text":
                        total += len(enc.encode(block.get("text", "")))
                    else:
                        import json
                        total += len(enc.encode(json.dumps(block)))
        # Name field
        if "name" in msg:
            total += len(enc.encode(msg["name"]))
    total += 2  # assistant priming
    return total


# ---------------------------------------------------------------------------
# Token budget tracker (from src/query/tokenBudget.ts)
# ---------------------------------------------------------------------------

@dataclass
class BudgetTracker:
    """Tracks token usage across continuations and decides when to stop.

    Source: src/query/tokenBudget.ts — BudgetTracker type + checkTokenBudget()

    Claude Code uses this to:
    - Track how many tokens each turn consumed
    - Detect diminishing returns (many continuations with tiny deltas)
    - Stop at ~90% of budget to leave room for the model's final answer
    """

    budget: int
    continuation_count: int = 0
    last_delta_tokens: int = 0
    cumulative_tokens: int = 0
    started_at: float = field(default_factory=time.time)
    _history: list[int] = field(default_factory=list)

    def record_turn(self, tokens_used: int) -> None:
        """Record token usage for a completed turn."""
        self.last_delta_tokens = tokens_used
        self.cumulative_tokens += tokens_used
        self.continuation_count += 1
        self._history.append(tokens_used)

    def check(self) -> BudgetDecision:
        """Decide whether to continue or stop.

        Source: src/query/tokenBudget.ts — checkTokenBudget()

        Rules:
        - Continue if cumulative < 90% of budget
        - Stop if 3+ continuations with < 500 token delta (diminishing returns)
        - Stop if at or over budget
        """
        threshold = int(self.budget * 0.9)

        if self.cumulative_tokens >= self.budget:
            return BudgetDecision(
                action="stop",
                reason=f"Budget exhausted: {self.cumulative_tokens}/{self.budget} tokens",
            )

        # Diminishing returns detection
        if self.continuation_count >= 3:
            recent = self._history[-3:]
            if all(d < 500 for d in recent):
                return BudgetDecision(
                    action="stop",
                    reason=(
                        f"Diminishing returns: last 3 turns used "
                        f"{recent} tokens each"
                    ),
                )

        if self.cumulative_tokens >= threshold:
            return BudgetDecision(
                action="stop",
                reason=(
                    f"At {self.cumulative_tokens}/{self.budget} tokens "
                    f"({self.cumulative_tokens * 100 // self.budget}%)"
                ),
            )

        return BudgetDecision(
            action="continue",
            reason=(
                f"{self.cumulative_tokens}/{self.budget} tokens "
                f"({self.cumulative_tokens * 100 // self.budget}%)"
            ),
        )


@dataclass
class BudgetDecision:
    """Result of a budget check."""

    action: Literal["continue", "stop"]
    reason: str


# ---------------------------------------------------------------------------
# Usage / context percentage helpers
# ---------------------------------------------------------------------------

@dataclass
class ContextUsage:
    """Token usage statistics for context window.

    Source: src/utils/context.ts — calculateContextPercentages()
    """

    used: int
    total: int

    @property
    def remaining(self) -> int:
        return max(0, self.total - self.used)

    @property
    def used_percent(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.used / self.total) * 100

    @property
    def remaining_percent(self) -> float:
        return 100.0 - self.used_percent


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Heuristic estimation
    sample = "Hello, world! This is a test of the token estimation system."
    print(f"Rough estimate: {rough_token_estimate(sample)} tokens")
    print(f"Accurate count: {count_tokens(sample)} tokens")

    # Message estimation
    msgs = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a Python function to sort a list."},
    ]
    print(f"\nMessage rough estimate: {rough_token_estimate_for_messages(msgs)} tokens")
    print(f"Message accurate count: {count_message_tokens(msgs)} tokens")

    # Budget tracker
    tracker = BudgetTracker(budget=10000)
    for turn_tokens in [3000, 2500, 2000, 400, 300, 200]:
        tracker.record_turn(turn_tokens)
        decision = tracker.check()
        print(f"\nTurn +{turn_tokens}: {decision.action} — {decision.reason}")
        if decision.action == "stop":
            break
