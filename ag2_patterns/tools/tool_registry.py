"""
Tool Registry — Registration, lookup, and management of tools for AG2 agents.

Extracted from Claude Code's tool system:
- src/tools.ts — getAllBaseTools(), getTools(), assembleToolPool()
- src/Tool.ts — Tool interface, buildTool() defaults
- src/constants/tools.ts — Tool allowlists for agents/modes

Patterns implemented:
1. Central tool registry with name-based lookup
2. Tool filtering by permissions, agent type, capability
3. Concurrent vs serial tool partitioning
4. AG2 function_map generation
5. Feature-gated tool loading
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from ag2_patterns.tools.schemas import (
    PermissionBehavior,
    PermissionResult,
    ToolDefinition,
)

logger = logging.getLogger(__name__)


# Type for a tool implementation function
ToolFunction = Callable[..., Any]

# Type for a permission checker
PermissionChecker = Callable[[str, dict[str, Any]], PermissionResult]


class ToolEntry:
    """A registered tool with its definition, implementation, and permission checker.

    Source: src/Tool.ts — Tool<Input, Output, P> type
    """

    def __init__(
        self,
        definition: ToolDefinition,
        implementation: ToolFunction,
        permission_checker: PermissionChecker | None = None,
        enabled: bool = True,
    ):
        self.definition = definition
        self.implementation = implementation
        self.permission_checker = permission_checker
        self.enabled = enabled

    @property
    def name(self) -> str:
        return self.definition.name

    def check_permissions(self, input_args: dict[str, Any]) -> PermissionResult:
        """Check if this tool call is allowed.

        Source: src/Tool.ts — checkPermissions()
        """
        if self.permission_checker:
            return self.permission_checker(self.name, input_args)
        return PermissionResult(behavior=PermissionBehavior.ALLOW)


class ToolRegistry:
    """Central registry for tools, supporting registration, lookup, and filtering.

    Source: src/tools.ts — getAllBaseTools(), getTools(), assembleToolPool()

    This mirrors Claude Code's approach where:
    - Tools are registered centrally
    - Filtered by permission mode and agent type
    - Partitioned into concurrent/serial groups for execution
    - Exposed as function_map to AG2 agents

    Example::

        registry = ToolRegistry()

        # Register a tool
        registry.register(
            ToolDefinition(name="read_file", description="Read a file", ...),
            implementation=my_read_file_fn,
        )

        # Get AG2 function_map
        function_map = registry.to_function_map()

        # Use with AG2 agent
        agent = AssistantAgent("coder", llm_config=llm_config)
        agent.register_function(function_map=function_map)
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolEntry] = {}
        self._aliases: dict[str, str] = {}
        self._deny_list: set[str] = set()
        self._allow_list: set[str] | None = None  # None = allow all

    def register(
        self,
        definition: ToolDefinition,
        implementation: ToolFunction,
        permission_checker: PermissionChecker | None = None,
        enabled: bool = True,
    ) -> None:
        """Register a tool.

        Source: src/tools.ts — tools are defined as module-level constants
        and collected in getAllBaseTools()
        """
        entry = ToolEntry(definition, implementation, permission_checker, enabled)
        self._tools[definition.name] = entry
        for alias in definition.aliases:
            self._aliases[alias] = definition.name

    def register_function(
        self,
        name: str,
        description: str,
        func: ToolFunction,
        parameters: list[dict[str, Any]] | None = None,
        is_read_only: bool = False,
        is_concurrency_safe: bool = False,
    ) -> None:
        """Convenience method to register a plain function as a tool.

        Simpler than constructing a ToolDefinition manually.
        """
        from ag2_patterns.tools.schemas import ToolParameter

        params = []
        if parameters:
            for p in parameters:
                params.append(ToolParameter(**p))

        defn = ToolDefinition(
            name=name,
            description=description,
            parameters=params,
            is_read_only=is_read_only,
            is_concurrency_safe=is_concurrency_safe,
        )
        self.register(defn, func)

    def get(self, name: str) -> ToolEntry | None:
        """Look up a tool by name or alias."""
        if name in self._tools:
            return self._tools[name]
        canonical = self._aliases.get(name)
        if canonical:
            return self._tools.get(canonical)
        return None

    def get_enabled_tools(self) -> list[ToolEntry]:
        """Get all enabled, non-denied tools.

        Source: src/tools.ts — getTools() filters by permission mode
        """
        result = []
        for entry in self._tools.values():
            if not entry.enabled:
                continue
            if entry.name in self._deny_list:
                continue
            if self._allow_list is not None and entry.name not in self._allow_list:
                continue
            result.append(entry)
        return result

    def set_deny_list(self, tool_names: set[str]) -> None:
        """Set tools that are denied.

        Source: src/constants/tools.ts — ALL_AGENT_DISALLOWED_TOOLS
        """
        self._deny_list = tool_names

    def set_allow_list(self, tool_names: set[str] | None) -> None:
        """Set allowlist (None = allow all).

        Source: src/constants/tools.ts — ASYNC_AGENT_ALLOWED_TOOLS
        """
        self._allow_list = tool_names

    def partition_for_execution(
        self, tool_calls: list[dict[str, Any]]
    ) -> list[list[dict[str, Any]]]:
        """Partition tool calls into batches: concurrent-safe vs serial.

        Source: src/services/tools/toolOrchestration.ts — partitionToolCalls()

        Strategy from Claude Code:
        - Consecutive read-only + concurrency-safe tools → one concurrent batch
        - Each non-safe tool → its own serial batch
        - Preserves ordering within each batch

        Args:
            tool_calls: List of dicts with at least {"name": ..., "arguments": ...}

        Returns:
            List of batches. Each batch is a list of tool calls that can
            be executed together (concurrent if len > 1).
        """
        batches: list[list[dict[str, Any]]] = []
        current_concurrent: list[dict[str, Any]] = []

        for call in tool_calls:
            entry = self.get(call.get("name", ""))
            if entry and entry.definition.is_concurrency_safe:
                current_concurrent.append(call)
            else:
                # Flush any accumulated concurrent calls
                if current_concurrent:
                    batches.append(current_concurrent)
                    current_concurrent = []
                # This call goes in its own batch
                batches.append([call])

        if current_concurrent:
            batches.append(current_concurrent)

        return batches

    def to_function_map(self) -> dict[str, ToolFunction]:
        """Generate AG2-compatible function_map from enabled tools.

        Returns:
            Dict mapping tool name → callable, ready for AG2's
            `agent.register_function(function_map=...)`.
        """
        return {entry.name: entry.implementation for entry in self.get_enabled_tools()}

    def to_tool_schemas(self) -> list[dict[str, Any]]:
        """Generate OpenAI-compatible tool schemas for enabled tools.

        Returns:
            List of function schemas for AG2's `tools` parameter.
        """
        return [entry.definition.to_function_schema() for entry in self.get_enabled_tools()]

    def to_ag2_tools(self) -> list[dict[str, Any]]:
        """Generate AG2 tool config (schemas + function_map combined).

        Returns:
            List of tool dicts with schema info for agent configuration.
        """
        return [entry.definition.to_ag2_tool_schema() for entry in self.get_enabled_tools()]

    @property
    def tool_names(self) -> list[str]:
        """List all registered tool names."""
        return [e.name for e in self.get_enabled_tools()]

    def __len__(self) -> int:
        return len(self.get_enabled_tools())

    def __contains__(self, name: str) -> bool:
        return self.get(name) is not None


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    registry = ToolRegistry()

    # Register some tools
    from ag2_patterns.tools.schemas import BUILTIN_TOOLS

    for tool_def in BUILTIN_TOOLS:
        registry.register(
            tool_def,
            implementation=lambda **kwargs: f"Mock result for {kwargs}",
        )

    print(f"Registered {len(registry)} tools: {registry.tool_names}")

    # Test partitioning
    calls = [
        {"name": "read_file", "arguments": {"file_path": "a.py"}},
        {"name": "grep", "arguments": {"pattern": "TODO"}},
        {"name": "bash", "arguments": {"command": "ls"}},
        {"name": "glob", "arguments": {"pattern": "*.py"}},
        {"name": "file_edit", "arguments": {"file_path": "a.py", "old_string": "x", "new_string": "y"}},
    ]
    batches = registry.partition_for_execution(calls)
    print(f"\nPartitioned {len(calls)} calls into {len(batches)} batches:")
    for i, batch in enumerate(batches):
        names = [c["name"] for c in batch]
        mode = "concurrent" if len(batch) > 1 else "serial"
        print(f"  Batch {i + 1} ({mode}): {names}")

    # Generate function_map
    fmap = registry.to_function_map()
    print(f"\nFunction map keys: {list(fmap.keys())}")

    # Generate schemas
    schemas = registry.to_tool_schemas()
    print(f"\nTool schemas ({len(schemas)}):")
    for s in schemas:
        print(f"  {s['function']['name']}: {s['function']['description'][:60]}...")
