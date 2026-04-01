"""
Context Window Manager — Auto-compaction and message management for AG2.

Extracted from Claude Code's context management system:
- src/services/compact/autoCompact.ts — Auto-compaction thresholds and triggers
- src/services/compact/compact.ts — Full conversation compaction
- src/services/compact/microCompact.ts — Lightweight tool-result clearing
- src/services/compact/prompt.ts — Compaction summary prompts
- src/utils/contextAnalysis.ts — Token usage analysis by category

Patterns implemented:
1. Auto-compaction threshold detection
2. Microcompaction (clear old tool results)
3. Full compaction via LLM summarization
4. Context analysis (token breakdown by category)
5. AG2 TransformMessages integration
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Protocol

from ag2_patterns.context.token_manager import (
    BudgetTracker,
    ContextUsage,
    count_message_tokens,
    rough_token_estimate,
    rough_token_estimate_for_messages,
)


# ---------------------------------------------------------------------------
# Constants (from src/services/compact/autoCompact.ts)
# ---------------------------------------------------------------------------

AUTOCOMPACT_BUFFER_TOKENS = 13_000
WARNING_THRESHOLD_BUFFER_TOKENS = 20_000
MANUAL_COMPACT_BUFFER_TOKENS = 3_000
COMPACT_MAX_OUTPUT_TOKENS = 20_000
MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3

# Post-compact reinject budgets (from src/services/compact/compact.ts)
POST_COMPACT_TOKEN_BUDGET = 50_000
POST_COMPACT_MAX_TOKENS_PER_FILE = 5_000

# Tools whose results can be safely cleared during microcompaction
COMPACTABLE_TOOLS = frozenset({
    "read_file", "bash", "grep", "glob",
    "web_search", "web_fetch", "file_edit", "file_write",
})


# ---------------------------------------------------------------------------
# Token warning states (from src/services/compact/autoCompact.ts)
# ---------------------------------------------------------------------------

class WarningLevel(str, Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    BLOCKING = "blocking"


@dataclass
class TokenWarningState:
    """Token usage warning state.

    Source: src/services/compact/autoCompact.ts — calculateTokenWarningState()
    """

    level: WarningLevel
    percent_used: float
    tokens_used: int
    context_window: int

    @property
    def tokens_remaining(self) -> int:
        return max(0, self.context_window - self.tokens_used)


def calculate_warning_state(
    tokens_used: int,
    context_window: int,
    max_output_tokens: int = COMPACT_MAX_OUTPUT_TOKENS,
) -> TokenWarningState:
    """Calculate token warning state.

    Source: src/services/compact/autoCompact.ts — calculateTokenWarningState()
    """
    effective_window = context_window - max_output_tokens
    auto_compact_threshold = effective_window - AUTOCOMPACT_BUFFER_TOKENS
    warning_threshold = auto_compact_threshold - WARNING_THRESHOLD_BUFFER_TOKENS
    blocking_limit = effective_window - MANUAL_COMPACT_BUFFER_TOKENS

    pct = (tokens_used / context_window * 100) if context_window > 0 else 0

    if tokens_used >= blocking_limit:
        level = WarningLevel.BLOCKING
    elif tokens_used >= auto_compact_threshold:
        level = WarningLevel.ERROR
    elif tokens_used >= warning_threshold:
        level = WarningLevel.WARNING
    else:
        level = WarningLevel.OK

    return TokenWarningState(
        level=level,
        percent_used=pct,
        tokens_used=tokens_used,
        context_window=context_window,
    )


# ---------------------------------------------------------------------------
# Context Analysis (from src/utils/contextAnalysis.ts)
# ---------------------------------------------------------------------------

@dataclass
class ContextAnalysis:
    """Breakdown of token usage by category.

    Source: src/utils/contextAnalysis.ts — analyzeContext()
    """

    tool_requests: dict[str, int] = field(default_factory=dict)
    tool_results: dict[str, int] = field(default_factory=dict)
    human_messages: int = 0
    assistant_messages: int = 0
    system_messages: int = 0
    total: int = 0


def analyze_context(messages: list[dict[str, Any]]) -> ContextAnalysis:
    """Analyze token distribution across message categories.

    Source: src/utils/contextAnalysis.ts — analyzeContext()
    """
    analysis = ContextAnalysis()
    for msg in messages:
        role = msg.get("role", "")
        tokens = rough_token_estimate(
            json.dumps(msg.get("content", ""))
        )

        if role == "system":
            analysis.system_messages += tokens
        elif role == "user":
            analysis.human_messages += tokens
        elif role == "assistant":
            content = msg.get("content", "")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "function_call":
                        name = block.get("name", "unknown")
                        analysis.tool_requests[name] = (
                            analysis.tool_requests.get(name, 0) + tokens
                        )
                    else:
                        analysis.assistant_messages += tokens
            else:
                analysis.assistant_messages += tokens
        elif role == "tool":
            name = msg.get("name", "unknown")
            analysis.tool_results[name] = (
                analysis.tool_results.get(name, 0) + tokens
            )

        analysis.total += tokens
    return analysis


# ---------------------------------------------------------------------------
# Microcompaction (from src/services/compact/microCompact.ts)
# ---------------------------------------------------------------------------

def microcompact(
    messages: list[dict[str, Any]],
    keep_last_n_tool_results: int = 5,
    compactable_tools: frozenset[str] = COMPACTABLE_TOOLS,
) -> tuple[list[dict[str, Any]], int]:
    """Clear old tool results to reclaim context space without LLM call.

    Source: src/services/compact/microCompact.ts — microcompactMessages()

    Strategy: Replace the content of old tool results from compactable tools
    with a short "[result cleared]" marker, keeping only the N most recent.

    Args:
        messages: The conversation messages.
        keep_last_n_tool_results: How many recent tool results to keep intact.
        compactable_tools: Set of tool names whose results can be cleared.

    Returns:
        Tuple of (modified messages, tokens freed estimate).
    """
    messages = copy.deepcopy(messages)
    tokens_freed = 0

    # Find all tool result indices for compactable tools
    tool_result_indices: list[int] = []
    for i, msg in enumerate(messages):
        if msg.get("role") == "tool" and msg.get("name") in compactable_tools:
            tool_result_indices.append(i)

    # Keep only the last N
    indices_to_clear = tool_result_indices[:-keep_last_n_tool_results] if keep_last_n_tool_results else tool_result_indices

    for idx in indices_to_clear:
        old_content = messages[idx].get("content", "")
        old_tokens = rough_token_estimate(
            old_content if isinstance(old_content, str) else json.dumps(old_content)
        )
        messages[idx]["content"] = "[result cleared to save context]"
        new_tokens = rough_token_estimate("[result cleared to save context]")
        tokens_freed += old_tokens - new_tokens

    return messages, tokens_freed


# ---------------------------------------------------------------------------
# Full Compaction via LLM (from src/services/compact/compact.ts)
# ---------------------------------------------------------------------------

# Compaction prompt template (from src/services/compact/prompt.ts)
COMPACT_PROMPT = """Summarize the conversation so far into a structured summary that preserves all critical context. Use this format:

1. **Primary Request**: What the user originally asked for
2. **Technical Context**: Key technical details, frameworks, languages, constraints
3. **Files Modified**: List of files created/edited with brief description of changes
4. **Errors Encountered**: Any errors and their resolutions
5. **Current Status**: What has been completed and what remains
6. **Key Decisions**: Important decisions made and their rationale
7. **Next Steps**: What should happen next

Be concise but preserve all information needed to continue the task without the original messages."""


class SummarizeFn(Protocol):
    """Protocol for the summarization function."""

    def __call__(self, messages: list[dict[str, Any]], prompt: str) -> str: ...


@dataclass
class CompactionResult:
    """Result of a full compaction.

    Source: src/services/compact/compact.ts — CompactionResult
    """

    summary: str
    messages_before: int
    messages_after: int
    tokens_before: int
    tokens_after_estimate: int


def compact_conversation(
    messages: list[dict[str, Any]],
    summarize_fn: SummarizeFn,
    context_window: int = 200_000,
    keep_last_n_messages: int = 4,
    custom_prompt: str | None = None,
) -> CompactionResult:
    """Compact a conversation by summarizing old messages via LLM.

    Source: src/services/compact/compact.ts — compactConversation()

    Flow:
    1. Split messages into [old_messages, recent_messages]
    2. Send old_messages to LLM with compaction prompt
    3. Replace old_messages with summary
    4. Return summary + recent messages

    Args:
        messages: Full conversation history.
        summarize_fn: Callable that takes messages + prompt → summary string.
        context_window: Total context window size.
        keep_last_n_messages: How many recent messages to keep verbatim.
        custom_prompt: Override the default compaction prompt.

    Returns:
        CompactionResult with the summary and stats.
    """
    if len(messages) <= keep_last_n_messages:
        return CompactionResult(
            summary="",
            messages_before=len(messages),
            messages_after=len(messages),
            tokens_before=rough_token_estimate_for_messages(messages),
            tokens_after_estimate=rough_token_estimate_for_messages(messages),
        )

    tokens_before = rough_token_estimate_for_messages(messages)

    # Split into old and recent
    old_messages = messages[:-keep_last_n_messages]
    recent_messages = messages[-keep_last_n_messages:]

    # Strip images from old messages before summarization
    # Source: src/services/compact/compact.ts — strips images/documents
    cleaned_old = _strip_images(old_messages)

    # Generate summary
    prompt = custom_prompt or COMPACT_PROMPT
    summary = summarize_fn(cleaned_old, prompt)

    # Build new message list
    tokens_after = rough_token_estimate(summary) + rough_token_estimate_for_messages(
        recent_messages
    )

    return CompactionResult(
        summary=summary,
        messages_before=len(messages),
        messages_after=1 + len(recent_messages),  # summary + recent
        tokens_before=tokens_before,
        tokens_after_estimate=tokens_after,
    )


def build_compacted_messages(
    result: CompactionResult,
    original_messages: list[dict[str, Any]],
    keep_last_n_messages: int = 4,
) -> list[dict[str, Any]]:
    """Build the new message list after compaction.

    Returns a list starting with the summary as a system message,
    followed by the recent messages.
    """
    if not result.summary:
        return original_messages

    recent = original_messages[-keep_last_n_messages:]
    summary_msg: dict[str, Any] = {
        "role": "user",
        "content": (
            f"[Previous conversation summary]\n\n{result.summary}\n\n"
            "[End of summary — continue from here]"
        ),
    }
    return [summary_msg] + recent


def _strip_images(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove image blocks from messages to save tokens during summarization."""
    result = []
    for msg in messages:
        msg = copy.copy(msg)
        content = msg.get("content", "")
        if isinstance(content, list):
            msg["content"] = [
                block
                for block in content
                if not (
                    isinstance(block, dict)
                    and block.get("type") in ("image_url", "image")
                )
            ]
        result.append(msg)
    return result


# ---------------------------------------------------------------------------
# AG2 Integration: TransformMessages-compatible transform
# ---------------------------------------------------------------------------

class ContextWindowTransform:
    """AG2-compatible message transform that manages context window.

    Use with AG2's `TransformMessages` or as a standalone transform.

    This implements the full Claude Code context management pipeline:
    1. Check if tokens exceed threshold
    2. Try microcompaction first (cheap, no LLM call)
    3. If still over, trigger full compaction

    Example with AG2::

        from autogen import AssistantAgent, TransformMessages
        from ag2_patterns.context.context_window import ContextWindowTransform

        transform = ContextWindowTransform(
            context_window=200_000,
            compact_threshold=0.85,
            summarize_fn=my_summarize_fn,
        )

        agent = AssistantAgent(
            "assistant",
            llm_config=llm_config,
            # AG2 >=0.4 supports transform_messages
        )
    """

    def __init__(
        self,
        context_window: int = 200_000,
        compact_threshold: float = 0.85,
        summarize_fn: SummarizeFn | None = None,
        keep_last_n_messages: int = 4,
        keep_last_n_tool_results: int = 5,
        model: str = "gpt-4o",
    ):
        self.context_window = context_window
        self.compact_threshold = compact_threshold
        self.summarize_fn = summarize_fn
        self.keep_last_n_messages = keep_last_n_messages
        self.keep_last_n_tool_results = keep_last_n_tool_results
        self.model = model
        self._compact_failures = 0

    def __call__(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Transform messages to fit within context window.

        Called by AG2's message processing pipeline before each LLM call.
        """
        token_count = rough_token_estimate_for_messages(messages)
        threshold = int(self.context_window * self.compact_threshold)

        if token_count < threshold:
            return messages

        # Step 1: Try microcompaction
        messages, freed = microcompact(
            messages,
            keep_last_n_tool_results=self.keep_last_n_tool_results,
        )
        token_count -= freed

        if token_count < threshold:
            return messages

        # Step 2: Full compaction (if summarize_fn provided)
        if self.summarize_fn and self._compact_failures < MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES:
            try:
                result = compact_conversation(
                    messages,
                    self.summarize_fn,
                    context_window=self.context_window,
                    keep_last_n_messages=self.keep_last_n_messages,
                )
                if result.summary:
                    self._compact_failures = 0
                    return build_compacted_messages(
                        result, messages, self.keep_last_n_messages
                    )
            except Exception:
                self._compact_failures += 1

        # Step 3: Hard truncation fallback — drop oldest messages
        while (
            rough_token_estimate_for_messages(messages) > threshold
            and len(messages) > self.keep_last_n_messages + 1
        ):
            # Keep system message at index 0 if present
            if messages[0].get("role") == "system" and len(messages) > 2:
                messages.pop(1)
            else:
                messages.pop(0)

        return messages

    def should_compact(self, messages: list[dict[str, Any]]) -> bool:
        """Check if messages should be compacted.

        Source: src/services/compact/autoCompact.ts — shouldAutoCompact()
        """
        token_count = rough_token_estimate_for_messages(messages)
        threshold = int(self.context_window * self.compact_threshold)
        return token_count >= threshold

    def get_usage(self, messages: list[dict[str, Any]]) -> ContextUsage:
        """Get current context usage stats."""
        used = rough_token_estimate_for_messages(messages)
        return ContextUsage(used=used, total=self.context_window)


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Create sample conversation
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Read the file main.py"},
        {
            "role": "assistant",
            "content": [
                {"type": "function_call", "name": "read_file", "arguments": '{"path": "main.py"}'}
            ],
        },
        {"role": "tool", "name": "read_file", "content": "x" * 5000},
        {"role": "assistant", "content": "The file main.py contains..."},
        {"role": "user", "content": "Now edit it to add error handling"},
        {"role": "assistant", "content": "I'll add try/except blocks..."},
    ]

    # Test context analysis
    analysis = analyze_context(messages)
    print(f"Context analysis — Total: {analysis.total} tokens")
    print(f"  Human: {analysis.human_messages}, Assistant: {analysis.assistant_messages}")
    print(f"  Tool results: {analysis.tool_results}")

    # Test microcompaction
    compacted, freed = microcompact(messages, keep_last_n_tool_results=0)
    print(f"\nMicrocompact freed ~{freed} tokens")

    # Test warning state
    state = calculate_warning_state(180_000, 200_000)
    print(f"\nWarning state at 180k/200k: {state.level.value} ({state.percent_used:.1f}%)")

    # Test transform
    transform = ContextWindowTransform(context_window=200_000, compact_threshold=0.85)
    usage = transform.get_usage(messages)
    print(f"\nContext usage: {usage.used}/{usage.total} ({usage.used_percent:.1f}%)")
    print(f"Should compact: {transform.should_compact(messages)}")
